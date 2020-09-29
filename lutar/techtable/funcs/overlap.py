# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:53 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : overlap.py
# @Desc   : overlapping indicators


import pandas as pd
import numpy as np
from inspect import isfunction


def ohlc4(df, **kwargs):
    s_val = df[["open", "high", "low", "close"]].mean(axis=1)
    s_val.name = "ohlc4"
    return s_val


def val_max_x(df, x, val="close", name_only=False, **kwargs):
    name = f"{val}_max{x}"
    if name_only:
        return name

    s_val = df[val].rolling(int(x)).max()
    s_val.name = name
    return s_val


def val_min_x(df, x, val="close", name_only=False, **kwargs):
    name = f"{val}_min{x}"
    if name_only:
        return name

    s_val = df[val].rolling(int(x)).min()
    s_val.name = name
    return s_val


def rx(df, x, col="close", name_only=False, **kwargs):
    """Return with window x: 将当前的col与 x天前的col比较，计算出的return。支持不同的col。"""
    name = f"r{x}" if col == "close" else f"r{x}_{col}"
    if name_only:
        return name

    s_val = df[col] / df[col].shift(x) - 1
    s_val.name = name
    return s_val


def lrx(df, x, name_only=False, **kwargs):
    """Lower Return with window x: 将当前的close与 max[x天前的close, x-1天前的open]比较，计算出的return"""
    name = f"lr{x}"
    if name_only:
        return name

    dft = df[["open", "close"]].copy()
    dft["next_open"] = dft.open.shift(-1)
    dft["high_ref"] = dft[["close", "next_open"]].max(axis=1)

    s_val = dft["close"] / dft["high_ref"].shift(x) - 1
    s_val.name = name
    return s_val


def grx(df, x, name_only=False, **kwargs):
    """Greater Return with window x: 将当前的close与 min[x天前的close, x-1天前的open]比较，计算出的return"""
    name = f"gr{x}"
    if name_only:
        return name

    dft = df[["open", "close"]].copy()
    dft["next_open"] = dft.open.shift(-1)
    dft["low_ref"] = dft[["close", "next_open"]].min(axis=1)

    s_val = dft["close"] / dft["low_ref"].shift(x) - 1
    s_val.name = name
    return s_val


def volma_x(df, x, name_only=False, **kwargs):
    name = f"volma{x}"
    if name_only:
        return name

    s_val = df["volume"].rolling(x).mean()
    s_val.name = name
    return s_val


def volma_dx(df, x, name_only=False, **kwargs):
    name = f"volma_d{x}"
    if name_only:
        return name

    s_volma_dx = df.loc[df.close < df.close.shift(), "volume"].rolling(x).mean()
    s_val = s_volma_dx.reindex(index=df.index).fillna(method="ffill")
    s_val.name = name
    return s_val


def volma_ux(df, x, name_only=False, **kwargs):
    """volume moving average of recent x up days"""
    name = f"volma_u{x}"
    if name_only:
        return name

    s_volma_ux = df.loc[df.close > df.close.shift(), "volume"].rolling(x).mean()
    s_val = s_volma_ux.reindex(index=df.index).fillna(method="ffill")
    s_val.name = name
    return s_val


def qrr_x(df, x, name_only=False, **kwargs):
    name = f"qrr_{x}"
    if name_only:
        return name

    s_val = df.volume / df.volume.rolling(x).mean().shift(-1)
    s_val.name = name
    return s_val


# ----keep at the end
_group = {
    k: v for k, v in locals().items() if isfunction(v) and v.__module__ == __name__
}
