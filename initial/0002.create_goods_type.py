#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, inspect
import django


if __name__ == "__main__":

    # add project dir to sys path
    fname = inspect.currentframe()
    folder = os.path.split(os.path.split(inspect.getfile(fname))[0])[0]
    if folder not in sys.path:
        sys.path.insert(0, folder)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

    from finance.models import GoodsType
    GoodsType.objects.get_or_create(name='1PTT')
    GoodsType.objects.get_or_create(name='PTT')
    GoodsType.objects.get_or_create(name='SERVICE')
