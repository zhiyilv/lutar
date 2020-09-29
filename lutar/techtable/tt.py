# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:54 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : tt.py
# @Desc   : The TechTable class

from lutar.commons import warnings
from lutar.techtable.funcs import func_dict

from functools import partial, update_wrapper
import pandas as pd


class TechTable:
    """


    """

    _df = None
    _raw_cols = None
    _verbose = None
    _alert_flag = {}

    def __init__(
        self, df=None, verbose=0, **kwargs,
    ):
        """

        * indexed with datetime is recommended


        """
        if df is not None:
            if isinstance(df, TechTable):
                df = df.df
            if isinstance(df, pd.DataFrame):
                if "datetime" in df.columns:
                    self._df = df.set_index("datetime")
                else:
                    self._df = df
        else:
            self._df = pd.DataFrame()

        self._raw_cols = self.df.columns.tolist()
        self._verbose = verbose
        for ti, func in func_dict.items():
            self.reg_func(ti_func=func, ti_name=ti)

    def reg_func(self, ti_func, ti_name=None):
        """
        ti_func must follow the standard format
        """
        ti_name = ti_name or ti_func.__name__
        super().__setattr__(
            ti_name.upper(), update_wrapper(partial(ti_func, self), ti_func)
        )

    @property
    def symbol_(self):
        return self.df.symbol.iat[0]

    @property
    def start_(self):
        return self.dt_index_[0]

    @property
    def end_(self):
        return self.dt_index_[-1]

    @property
    def dt_index_(self):
        return self.df.index

    @property
    def funcs_(self):
        return sorted([x for x in self.__dict__.keys() if x.isupper()])

    @property
    def df(self):
        return self._df

    @property
    def raw(self):
        return self.df.loc[:, self._raw_cols] if self._raw_cols else None

    def aligned(self, calendar=None, dfi=None):
        """align to a calendar, or according to the index

        * if align to dfi, the dates after self.df.dt_index_[-1] is ignored
        """
        if calendar is None:
            start_ts = max(self.dt_index_[0], dfi.dt_index_[0])
            end_ts = min(self.dt_index_[-1], dfi.dt_index_[-1])
            calendar = dfi.loc[start_ts:end_ts].index

        # 对齐
        earliest = self.df.index[0]
        calendar = calendar[calendar >= earliest]

        dfs_aligned = self.raw.reindex(index=calendar)
        dfs_aligned.symbol = dfs_aligned.symbol.fillna(self.symbol_)

        # 填充
        for col in ["volume", "turnover"]:
            try:
                dfs_aligned[col] = dfs_aligned[col].fillna(0)
            except KeyError:
                pass

        # use the last valid close to fill the subsequent nan
        dfs_aligned.close = dfs_aligned.close.fillna(method="ffill")
        for col in ["open", "high", "low"]:
            try:
                dfs_aligned[col] = dfs_aligned[col].fillna(dfs_aligned.close)
            except KeyError:
                pass

        # use the first valid open to fill all previous nan
        if dfs_aligned.index[0] > calendar[0]:
            dfs_aligned.open = dfs_aligned.open.fillna(method="bfill")
            for col in ["high", "low", "close"]:
                try:
                    dfs_aligned[col] = dfs_aligned[col].fillna(dfs_aligned.open)
                except KeyError:
                    pass
        return TechTable(dfs_aligned)

    def save(self, df_ti, cols=True):
        if isinstance(cols, bool) and cols:
            for c in df_ti.columns:
                c = str(c)
                if c not in self.raw.columns:
                    self.df.loc[df_ti.index, c] = df_ti[c]

        if isinstance(cols, str):
            self.df.loc[df_ti.index, cols] = df_ti[cols]
        if isinstance(cols, list):
            for c in cols:
                c = str(c)
                if c in df_ti.columns:
                    self.df.loc[df_ti.index, c] = df_ti[c]

    def __getattr__(self, item):
        # item不是TT的attribute，进入此函数
        if self.df is None:
            return None

        ITEM = item.upper()
        try:
            result = self.df.__getattr__(item)  # 优先尝试从self.df中读取现有数据
            if self._verbose > 0 and ITEM in self.__dict__.keys():
                if self._alert_flag.get(ITEM, True):
                    self._alert_flag[ITEM] = False  # only warn once
                    conflict_alert = (
                        f"The indicator function {item} is in conflict with internal df's attribute/column name. "
                        f"Returning TechTable.df.{item}.\n"
                        f"Use TechTable.{ITEM} to access the indicator function.\n"
                    )
                    warnings.warn(conflict_alert, UserWarning)
            return result
        except AttributeError:  # item 既不在TT的attribute中，又不在self.df的attribute中
            result = self.__dict__.get(ITEM, None)
            if result is None:
                indicator_alert = f"{item} is not in the internal df or the Indicator {ITEM} is not supported yet."
                raise KeyError(indicator_alert)

            # feature-generation function, return the function
            if ITEM.startswith("LHGEN_"):
                return result

            # 无需额外参数的ti，如ohlc4，第一次调用的时候自动计算
            # 尝试获取默认列名，如果不能获取，说明需要更多的参数，即应返回函数
            try:
                ti_col = result(name_only=True)
                s_ti = result(name_only=False)
                if isinstance(s_ti, pd.Series):  # normally should be series
                    self.df[ti_col] = s_ti
                return s_ti
            except:
                return result

    def __setattr__(self, key, value):
        if key in ["_raw_cols", "_df", "_area", "_alert_flag", "_verbose"]:
            super().__setattr__(key, value)

        elif key.upper() in self.__dict__.keys():
            msg = (
                f"Cannot set the '{key}' since it is an internal Technical Indicator. "
                f"Consider using tt['{key}'] to modify the column."
            )
            raise KeyError(msg)
        else:
            self._df.__setattr__(key, value)

    def __getitem__(self, item):
        return self.df.__getitem__(item)

    def __setitem__(self, key, value):
        return self.df.__setitem__(key, value)

    def __repr__(self):
        return self.df.__repr__()

    def __getstate__(self):
        return self.df, self._raw_cols, self._verbose, self._alert_flag

    def __setstate__(self, state):
        # self._df = state[0]
        # self._raw_cols = state[1]
        # self._verbose = state[2]
        # self._alert_flag = state[3]

        self._df, self._raw_cols, self._verbose, self._alert_flag = state

        for ti, func in func_dict.items():
            self.reg_func(ti_func=func, ti_name=ti)


# ----keep at the end
