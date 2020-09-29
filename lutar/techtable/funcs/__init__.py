# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:53 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : __init__.py.py
# @Desc   : The funcs package's init file


import os
from inspect import isfunction
from lutar.commons import magicdf

func_dict = {}

for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if f.endswith(".py") and f != "__init__.py":
        m = f[:-3]
        mod = __import__(".".join([__name__, m]), fromlist=[m])

        for k, v in mod.__dict__.items():
            if isfunction(v) and v.__module__ == mod.__name__ and not k.startswith("_"):
                func_dict[k] = magicdf(v)

__all__ = ["func_dict"]


# ----keep at the end
