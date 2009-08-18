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

from snipperize.snippet.models import Snippet
from snipperize.snippet.models import Tag

import settings

class TagCoefManager(models.Manager):
    
    counts = {}
    
    def update_correlations(self, offset):
        self.count_tags()
        tags = Tag.all().fetch(10, int(offset))
        if not tags: return
        all_tags = Tag.all()
        for tag in all_tags:
            self.get_tag_relations(tag, all_tags)
        
        
    def get_tag_relations(self, tag, tags):
        c1 = self.counts[tag.key().id()]
        tc = TagCoef.all().filter('tag', tag.key())
        if tc: db.delete(tc)
        for t in tags:
            if tag.key().id() == t.key().id():
                distance = 0.0
            else:
                c2 = self.counts[t.key().id()]
                shr = self.count_both(tag, t)
                distance = 1.0-(float(shr)/(c1+c2-shr))
            if distance < 1:
                tc = TagCoef(tag=tag, related_tag=t, distance=distance)
                tc.put()
    
    def count_tags(self):
        for t in Tag.all():
            self.counts[t.key().id()] = self.count_tag(t)
        return self.counts
        
    def count_tag(self, tag):
        return Snippet.all().filter('tags', tag.key()).count()
    
    def count_both(self, ta, tb):
        return Snippet.all().filter('tags', ta.key()).filter('tags', tb.key()).count()
    
class TagCoef(db.Model):
    tag = db.ReferenceProperty(Tag, collection_name='tag_collection')
    related_tag = db.ReferenceProperty(Tag, collection_name='related_tag_collection')
    distance = db.FloatProperty()
    
    objects = TagCoefManager()