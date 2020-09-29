# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:52 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : parallel.py
# @Desc   : for Parallelization

import joblib
from inspect import signature


def job_factory(
    func, feeder, parallel: joblib.Parallel = None, **kwargs,
):
    """
    parallel run func with data provided by feeder

    :param func:
    :param feeder:
    :param parallel:
    :param kwargs:
    :return:
    """
    kwargs = {
        k: v
        for k, v in kwargs.items()
        if k in signature(joblib.Parallel).parameters.keys()
    }
    if parallel is None:
        # hack on n_jobs to avoid unnecessary overhead
        n_jobs = kwargs.get("n_jobs", -1)
        if n_jobs < 0:
            n_jobs = joblib.cpu_count() + n_jobs + 1

        # retricted by total
        try:
            total = feeder.total
            n_jobs = min(n_jobs, total)
        except:
            pass

        kwargs["n_jobs"] = n_jobs

        # shortcut when 1
        if n_jobs == 1:
            return [func(i) for i in feeder]

        parallel = joblib.Parallel(**kwargs)
    return parallel(joblib.delayed(func)(i) for i in feeder)


# ----keep at the end
