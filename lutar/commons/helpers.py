# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:51 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : helpers.py
# @Desc   : useful funcs and decorators

import warnings
from functools import wraps
import inspect
import pandas as pd

from .parallel import job_factory


def resolve_irange(
    istart, iend, i_max=None, i_min=0, start=None, end=None, dt_index=None
):
    """
    Decide the real istart and iend
    """
    if i_max is None:
        i_max = dt_index.size - 1

    istart_list = []
    if istart:
        if istart < 0:
            istart = i_max + 1 + istart
        istart_list.append(istart)

    if start:
        try:
            real_start = dt_index[dt_index >= start][0]
            istart2 = dt_index.get_loc(real_start)
        except IndexError:
            # cannot find real_start since no days >= start
            # no data to calculate
            istart2 = i_max + 1
        except TypeError:
            # cannot compare
            # no constraint induced
            istart2 = 0
        istart_list.append(istart2)

    # use the earlier istart
    istart = max(i_min, min(istart_list) if istart_list else 0)

    iend_list = []
    if iend:
        if iend < 0:
            iend = i_max + 1 + iend
        iend_list.append(iend)

    if end:
        try:
            real_end = dt_index[dt_index <= end][-1]
            iend2 = dt_index.get_loc(real_end)
        except IndexError:
            iend2 = i_min - 1
        except TypeError:
            iend2 = i_max
        iend_list.append(iend2)

    iend = min(i_max, max(iend_list) if iend_list else i_max)
    return istart, iend


# -------- warnings
def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return f"{msg}\n"


warnings.formatwarning = custom_formatwarning
# warnings.simplefilter(action="ignore", category=FutureWarning)


def missing_warning(cols_needed, df_columns, ti_name, msg=""):
    missing_list = []
    for c in cols_needed:
        if c not in df_columns:
            missing_list.append(c)
    if missing_list:
        value_missing = f"Fields: {missing_list} cannot be found. Needed by {ti_name.upper()}. \n{msg}\n"
        warnings.warn(value_missing)
        return True

    return False


# -------- warnings

# -------- decorators
def magicdf(func):
    """
    # This decorator enables the following functions:

    * Accept TechTable so that all funcs can be directly accessed
    * Enable 'name_only'/'fresh'/'save' for those func without the parameter
    * Return the result directly if it already exists as a column

    # Parameters

    * name_only: only return the unique name of the generated series
    * fresh: force re-calculate values by the func
    * save: save into the original dataframe

    # standard format of func

    ```
    def func(df, x, param1="aaa", param2='bbb', name_only=False, **kwargs):
        name = f"r{x}"
        if name_only:
            return name


        s_val = ... # main logic
        s_val.name = name
        return s_val
    ```

    """

    @wraps(func)
    def wrapper(df, *args, **kwargs):
        # shortcut for gen funcs
        if func.__name__.startswith("lhgen_"):
            return func(df=df, *args, **kwargs)

        func_sig = inspect.signature(func)
        trans_inputs = func_sig.bind(df, *args, **kwargs)
        trans_inputs.apply_defaults()
        input_dict = {}
        for k, v in trans_inputs.arguments.items():
            if k != "kwargs":
                input_dict[k] = v
            else:
                input_dict.update(v)

        # auto-save
        # 1. get the name
        flag_name_only = input_dict.get("name_only", False)  # 临时保存
        if "name_only" not in func_sig.parameters:  # 名字固定的TI，无需设置name_only参数
            ti_name = func.__name__
        else:
            input_dict["name_only"] = True
            ti_name = func(**input_dict)

        if flag_name_only:
            return ti_name

        # 2. get the value
        if ti_name in df.columns and not input_dict.get("fresh", False):
            return df[ti_name]

        # re-calculate
        input_dict["name_only"] = False
        result = func(**input_dict)

        # 3. save
        if input_dict.get("save", True) and isinstance(result, pd.Series):
            df[ti_name] = result
        return result

    return wrapper


# -------- decorators

# ----keep at the end
