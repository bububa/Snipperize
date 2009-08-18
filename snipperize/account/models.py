# -*- coding: utf-8 -*-
import re
from django.db.models import permalink
from django.db import models

from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery
from google.appengine.ext.db import polymodel
from google.appengine.ext import search

from google.appengine.api import users

from google.appengine.api import memcache

import settings
        

class UserPref(db.Model):
    user = db.UserProperty(required=True)
    email = db.EmailProperty(required=False, verbose_name=u'Email')
    api_key = db.StringProperty(unicode)
    registered_at = db.DateTimeProperty(auto_now_add=True)
    
    def __unicode__(self):
        return self.user.nickname()
        
    @permalink
    def get_absolute_url(self):
        return ('user_detail', None, {'user_id': self.key().id()})
    
    @permalink
    def get_snippets_url(self):
        return ('user_snippets', None, {'user_id': self.key().id()})
        
    @staticmethod
    def get_or_insert_by_user(user):
        if not user: return None
        res = UserPref.gql("WHERE email=:1", user.email())
        if res.get(): return res.get()
        new_user = UserPref(user=user, email=user.email())
        new_user.put()
        return new_user