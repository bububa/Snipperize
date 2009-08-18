# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from snipperize.account.models import UserPref
from snipperize.snippet.models import Snippet
from snipperize.snippet.models import Tag
import settings

class LatestSnippets(Feed):
    title = u'Latest Snippets - Snipperize'
    link = '/feeds/latest/'
    description = u'The latest snippets on snipperize'
        
    def items(self):
        return Snippet.all().order('-published_at')[:50]
    
    def item_author_name(self, item):
        return item.author.user.nickname()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return settings.SITE_DOMAIN + item.author.get_absolute_url()
    
    def item_link(self, item):
        return settings.SITE_DOMAIN + item.get_absolute_url()
        
    def item_pubdate(self, item):
        return item.published_at
    
    def item_categories(self, item):
        return (item.language,)
        

class UserSnippets(Feed):
    
    def get_object(self, user_ids):
        if len(user_ids) != 1: raise ObjectDoesNotExist
        return UserPref.get_by_id(int(user_ids[0]))

    def title(self, obj):
        return "Latest Snippets of %s - Snipperize" % obj.user.nickname()

    def link(self, obj):
        if not obj: raise FeedDoesNotExist
        return settings.SITE_DOMAIN + obj.get_absolute_url()

    def description(self, obj):
        return "The latest snippets of %s on snipperize" % obj.user.nickname()
    
    def author_name(self, obj):
        return obj.user.nickname()
    
    def author_email(self, obj):
        return obj.email
    
    def author_link(self, obj):
        return settings.SITE_DOMAIN + obj.get_absolute_url()

    def items(self, obj):
        return Snippet.all().filter('author', obj.key()).order('-published_at')[:50]
    
    def item_author_name(self, item):
        return item.author.user.nickname()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return settings.SITE_DOMAIN + item.author.get_absolute_url()
    
    def item_link(self, item):
        return settings.SITE_DOMAIN + item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_categories(self, item):
        return (item.language,)

class LanguageSnippets(Feed):
    
    def get_object(self, langs):
        if len(langs) != 1: raise ObjectDoesNotExist
        return langs[0]

    def title(self, obj):
        return "Latest Snippets of %s - Snipperize" % obj

    def link(self, obj):
        if not obj: raise FeedDoesNotExist
        return settings.SITE_DOMAIN + reverse('language_snippets', kwargs={'language':obj})

    def description(self, obj):
        return "The latest snippets of %s on snipperize" % obj

    def items(self, obj):
        return Snippet.all().filter('language', obj).order('-published_at')[:50]
    
    def item_author_name(self, item):
        return item.author.user.nickname()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return settings.SITE_DOMAIN + item.author.get_absolute_url()
    
    def item_link(self, item):
        return settings.SITE_DOMAIN + item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_categories(self, item):
        return (item.language,)

class TagSnippets(Feed):
    
    def get_object(self, tags):
        if len(tags) != 1: raise ObjectDoesNotExist
        return Tag.get_by_id(int(tags[0]))

    def title(self, obj):
        return "Latest Snippets of %s - Snipperize" % obj.name

    def link(self, obj):
        if not obj: raise FeedDoesNotExist
        return settings.SITE_DOMAIN + reverse('tag_snippets', kwargs={'tag_name':obj.get_escape_name(), 'tag_id':obj.key().id()})

    def description(self, obj):
        return "The latest snippets of %s on snipperize" % obj.name

    def items(self, obj):
        return Tag.objects.snippets(obj)[:50]
    
    def item_author_name(self, item):
        return item.author.user.nickname()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return settings.SITE_DOMAIN + item.author.get_absolute_url()
    
    def item_link(self, item):
        return settings.SITE_DOMAIN + item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_categories(self, item):
        return (item.language,)

class LanguageTagSnippets(Feed):
    
    def get_object(self, rs):
        if len(rs) != 2: raise ObjectDoesNotExist
        return (rs[0], Tag.get_by_id(int(rs[1])))

    def title(self, obj):
        return "Latest Snippets of %s talking about %s - Snipperize" % (obj[0], obj[1].name)

    def link(self, obj):
        if not obj: raise FeedDoesNotExist
        return settings.SITE_DOMAIN + reverse('language_tag_snippets', kwargs={'language':obj[0], 'tag_name':obj[1].get_escape_name(), 'tag_id':obj[1].key().id()})

    def description(self, obj):
        return "The latest snippets of %s talking about %s on snipperize" % (obj[0], obj[1].name)

    def items(self, obj):
        snippets = Tag.objects.snippets(obj[1])
        snippets = snippets.filter('language', obj[0]).order('-published_at')
        return snippets[:50]
    
    def item_author_name(self, item):
        return item.author.user.nickname()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return settings.SITE_DOMAIN + item.author.get_absolute_url()
    
    def item_link(self, item):
        return settings.SITE_DOMAIN + item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_categories(self, item):
        return (item.language,)