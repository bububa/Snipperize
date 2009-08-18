# -*- coding: utf-8 -*-
import logging
import datetime
import time
import re

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template.context import RequestContext
from django.core.urlresolvers import reverse

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.db import GqlQuery
from google.appengine.ext import db

from snipperize.task.models import TagCoefManager

import settings

def update_tag_correlations(request, offset):
    
    tm = TagCoefManager()
    tm.update_correlations(offset)
    
    return HttpResponse('Update finished', content_type='text/html')