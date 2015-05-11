# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from celery import shared_task

from .gen_tiles import gen_tiles


@shared_task
def generate_tiles(*args, **kwargs):
    return gen_tiles(*args, **kwargs)
