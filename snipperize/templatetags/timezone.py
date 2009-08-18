# -*- coding: utf8 -*-
from django import template
from datetime import timedelta
import datetime

register = template.Library()

def timezone(value, offset):
    return value + timedelta(hours=offset)
register.filter(timezone)