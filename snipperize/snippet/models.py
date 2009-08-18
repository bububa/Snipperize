# -*- coding: utf-8 -*-
import re
from datetime import datetime
from datetime import timedelta

from django.db.models import permalink
from django.db import models

from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery
from google.appengine.ext.db import polymodel
from google.appengine.ext import search
from google.appengine.api import mail

from google.appengine.api import users

from google.appengine.api import memcache

from snipperize.account.models import UserPref
from snipperize.utils.webutils import safe_url

from markdown import Markdown
import settings
    
class TagManager(models.Manager):
    def get_by_name(self, name):
        rs = Tag.gql("WHERE name=:1", name)
        return rs.get()
        
    def snippets(self, tag):
        return Snippet.all().filter('tags', tag.key()).order('-published_at')
        

class Tag(db.Model):
    name = db.StringProperty(unicode)
    number = db.IntegerProperty(default=1)
    inserted_at = db.DateTimeProperty(auto_now=True)
    languages = db.ListProperty(unicode, verbose_name=u'Language')
    objects = TagManager()
    
    def __unicode__(self):
        return self.name
        
    @permalink
    def get_absolute_url(self):
        return ('tag_snippets', None, {'name': safe_url(self.name), 'tag_id': self.key().id()})
    
    def get_escape_name(self):
        return safe_url(self.name)
    

class UserTag(db.Model):
    user = db.ReferenceProperty(UserPref)
    number = db.IntegerProperty(default=1)
    tag = db.ReferenceProperty(Tag)
    
          
class SnippetManager(models.Manager):
    
    def add_snippet(self, title, language, comment, url, tags, code, private, profile_callback=None):
        snippet = Snippet(title=title, language=language, code=code)
        if comment: snippet.comment = comment
        if private: snippet.private = True
        if url: snippet.url = url
        snippet.author = UserPref.get_or_insert_by_user(users.get_current_user())
        if tags:
            for t in tags.split(','):
                t = t.strip()
                if not t: continue
                tag = Tag.objects.get_by_name(name=t)
                if not tag:
                    tag = Tag(name=t)
                    tag.languages.append(language)
                    tag.put()
                    userTag = UserTag(user=snippet.author, tag=tag)
                else:
                    tag.number += 1
                    if language not in tag.languages:
                        tag.languages.append(language)
                    tag.put()
                    res = UserTag.gql("WHERE user=:1 and tag=:2", snippet.author, tag)
                    userTag = res.get()
                    if userTag: 
                        userTag.number += 1
                    else:
                        userTag = UserTag(user=snippet.author, tag=tag)
                userTag.put()
                snippet.tags.append(tag.key())
        snippet.put()
        
        subversion = Subversion(snippet=snippet, title=snippet.title, language=snippet.language, code=snippet.code)
        if comment: subversion.comment = comment
        if url: subversion.url = url
        subversion.put()
        return snippet
    
    def edit_snippet(self, snippet_id, title, language, comment, url, tags, code, private, profile_callback=None):
        snippet = Snippet.get_by_id(snippet_id)
        snippet.title = title
        snippet.code = code
        if comment: snippet.comment = comment
        if private: snippet.private = True
        if url: snippet.url = url
        
        old_tags = db.get(snippet.tags)
        if old_tags:
            for t in old_tags:
                if not t: continue
                res = UserTag.gql("WHERE user=:1 and tag=:2", snippet.author, t)
                userTag = res.get()
                if t.number: t.number -= 1
                if t.number <= 1: 
                    t.delete()
                    if userTag: userTag.delete()
                    continue
                elif not userTag:
                    userTag = UserTag(user=snippet.author, tag=t)
                    userTag.put()
                if t.number > 1 and snippet.language != language:
                    old_languages = t.languages
                    t.languages = []
                    for l in old_languages:
                        if l != snippet.language: t.languages.append(l)
                t.put()
                        
        snippet.tags = []
        for t in tags.split(','):
            t = t.strip()
            if not t: continue 
            tag = Tag.objects.get_by_name(name=t)
            if not tag:
                tag = Tag(name=t)
                tag.languages.append(language)
                tag.put()
                userTag = UserTag(user=snippet.author, tag=tag)
            else:
                tag.number += 1
                if language not in tag.languages:
                    tag.languages.append(language)
                tag.put()
                res = UserTag.gql("WHERE user=:1 and tag=:2", snippet.author, tag)
                userTag = res.get()
                if userTag: 
                    userTag.number += 1
                else:
                    userTag = UserTag(user=snippet.author, tag=tag)
            userTag.put()
            snippet.tags.append(tag.key())
        
        snippet.language = language
        snippet.put()
        
        subversion = Subversion(snippet=snippet, title=snippet.title, language=snippet.language, code=snippet.code)
        if comment: subversion.comment = comment
        if url: subversion.url = url
        subversion.put()
        return snippet
    
    def delete_snippet(self, snippet_id):
        snippet = Snippet.get_by_id(int(snippet_id))
        if not snippet: return None
        subversions = snippet.get_subversions()
        db.delete(subversions)
        old_tags = db.get(snippet.tags)
        if old_tags:
            for t in old_tags:
                if not t: continue
                res = UserTag.gql("WHERE user=:1 and tag=:2", snippet.author, t)
                userTag = res.get()
                if userTag:
                    if userTag.number <=1: 
                        userTag.delete()
                    else:
                        userTag.number -= 1
                        userTag.put()
                if t.number: t.number -= 1
                if t.number <= 0: 
                    t.delete()
                    continue
                if t.number > 0:
                    old_languages = t.languages
                    t.languages = []
                    for l in old_languages:
                        if l != snippet.language: t.languages.append(l)
                t.put()
        language = snippet.language
        snippet.delete()
        return language
                
    def language_snippets(self, language):
        return Snippet.all().filter('language', language)
    
    def strip_html_tags(self, text):
        strip = ('head', 'style', 'script', 'object', 'embed', 'applet', 'noframes', 'noscript', 'noembed')
        for tag in strip:
            pattern = re.compile('<%s*?>.*?</%s>' % (tag, tag), re.S | re.I | re.U)
            text = re.sub(pattern, ' ', text)
        
        linebreak = ('address', 'blockquote', 'center', 'del',
                    'div', 'h[1-9]', 'ins', 'isindex', 'p', 'pre',
                    'dir', 'dl', 'dt', 'dd', 'li', 'menu', 'ol', 'ul',
                    'table', 'th', 'td', 'caption',
                    'form', 'button', 'fieldset', 'legend', 'input',
                    'label', 'select', 'optgroup', 'option', 'textarea',
                    'frameset', 'frame', 'iframe')
        
        for tag in linebreak:
            pattern = re.compile('(</?%s)' % tag, re.I | re.U)
            text = re.sub(pattern, '\n\\1', text)
        
        return text


class Snippet(search.SearchableModel):
    author = db.ReferenceProperty(UserPref)
    title = db.StringProperty(verbose_name=u'Title')
    language = db.StringProperty(choices=set(settings.SUPPORT_LANGUAGES), verbose_name=u'Language')
    comment = db.TextProperty(verbose_name=u'Comment')
    url = db.LinkProperty(required=False, verbose_name=u'URL')
    published_at = db.DateTimeProperty(auto_now_add=True)
    modified_at = db.DateTimeProperty(auto_now=True)
    tags = db.ListProperty(db.Key, verbose_name=u'Tag')
    code = db.TextProperty(verbose_name=u'Code')
    private = db.BooleanProperty(default=False, verbose_name=u'Private')
    
    objects = SnippetManager()
    
    def __unicode__(self):
        return self.title
    
    @permalink
    def get_absolute_url(self):
        return ('snippet_detail', None, {
            'snippet_language': self.language,
            'snippet_title': safe_url(self.title),
            'snippet_id': self.key().id()
        })
    
    @permalink
    def get_edit_url(self):
        return ('snippet_edit', None, {
            'snippet_id': self.key().id()
        })
    
    @permalink
    def get_delete_url(self):
        return ('snippet_delete', None, {
            'snippet_id': self.key().id()
        })
    
    def elapsed(self):
        now = datetime.now()
        delta = now - self.published_at
        days = delta.days
        hours = float(delta.seconds)/3600
        return {'days':days, 'hours':hours}
    
    def markdown_comment(self):
        if not self.comment: return self.comment
        md = Markdown()
        return md.convert(self.comment)
            
    def get_language(self):
        for k, v in settings.SUPPORT_LANGUAGES.items():
            if k == self.language: return {'name':v, 'key':k}
        return None
        
    def get_tags(self):
        return db.get(self.tags)
        
    def get_subversions(self):
        subversions = Subversion.all().filter('snippet', self).order('-published_at')
        return subversions
    
    def get_comments(self):
        comments = Comment.all().filter('snippet', self).order('-writed_at')
        return comments
    
    def is_editable(self):
        user = users.get_current_user()
        if not user: return None
        uemail = user.email().lower()
        return self.author.email == uemail or uemail in (x[1] for x in settings.ADMINS)
    
    def is_fav(self):
        userPref = UserPref.get_or_insert_by_user(users.get_current_user())
        if not userPref: return None
        return UserFavSnippet.gql("WHERE user=:1 and snippet=:2", userPref, self).count()
        
    def add_comment(self, message):
        comment = Comment()
        comment.content = message
        comment.author = UserPref.get_or_insert_by_user(users.get_current_user())
        comment.snippet = self
        comment.subversion = Subversion.all().filter('snippet', self).order('-published_at').get()
        comment.put()

        mail.send_mail(sender=settings.DEFAULT_FROM_EMAIL,
                        to=self.author.email,
                        subject=(u'Syd, your snippet %s has a new comment.'%self.title).encode('utf8'),
                        body=(u'''%s write a message under your snippet %s:
                        %s
                        Click here to give response: %s''' %(comment.author,
                        self.title, comment.content, settings.SITE_DOMAIN + self.get_absolute_url())).encode('utf8')
                        )
        return comment


class Subversion(db.Model):
    title = db.StringProperty(verbose_name=u'Title')
    language = db.StringProperty(choices=set(settings.SUPPORT_LANGUAGES), verbose_name=u'Language')
    comment = db.TextProperty(verbose_name=u'Comment')
    url = db.LinkProperty(required=False, verbose_name=u'URL')
    published_at = db.DateTimeProperty(auto_now_add=True)
    code = db.TextProperty(verbose_name=u'Code')
    snippet = db.ReferenceProperty(Snippet)
    
    def __unicode__(self):
        return ''.join(['r', str(self.key().id())])
    
    @permalink
    def get_absolute_url(self):
        return ('snippet_subversion_detail', None, {
            'snippet_language': self.language,
            'snippet_title': safe_url(self.title),
            'snippet_id': self.snippet.key().id(),
            'subversion_id': self.key().id()
        })
        
    def get_language(self):
        for k, v in settings.SUPPORT_LANGUAGES.items():
            if k == self.language: return {'name':v, 'key':k}
        return None
    
    @staticmethod
    def delete_subversion(self, subversion_id):
        subversion = Subversion.get_by_id(int(subversion_id))
        if not subversion: return None
        subversion.delete()
    
    def elapsed(self):
        now = datetime.now()
        delta = now - self.published_at
        days = delta.days
        hours = float(delta.seconds)/3600
        return {'days':days, 'hours':hours}

    def markdown_comment(self):
        if not self.comment: return self.comment
        md = Markdown()
        return md.convert(self.comment)
    
    def get_comments(self):
        comments = Comment.all().filter('subversion', self).order('-writed_at')
        return comments

    def add_comment(self, message):
        comment = Comment()
        comment.content = message
        comment.author = UserPref.get_or_insert_by_user(users.get_current_user())
        comment.subversion = self
        comment.snippet = self.snippet
        comment.put()

        mail.send_mail(sender="thepeppersstudio@gmail.com",
                        to=self.author.email,
                        subject=(u'Syd, your snippet %s version r%d has a new comment.'%(self.title, self.key().id())).encode('utf8'),
                        body=(u'''%s write a message under your snippet %s version r%d:
                        %s
                        点击这个链接回复: %s''' %(comment.author,
                        self.title, self.key().id(), comment.content, settings.SITE_DOMAIN + self.get_absolute_url())).encode('utf8')
                        )
        return comment
    
class Comment(db.Model):
    author = db.ReferenceProperty(UserPref)
    snippet = db.ReferenceProperty(Snippet)
    subversion = db.ReferenceProperty(Subversion)
    content = db.StringProperty(multiline=True)
    writed_at = db.DateTimeProperty(auto_now_add=True)
    
    def elapsed(self):
        now = datetime.now()
        delta = now - self.writed_at
        days = delta.days
        hours = float(delta.seconds)/3600
        return {'days':days, 'hours':hours}


class SnippetVisitLogManager(models.Manager):
    
    def log(self, snippet):
        visitor = UserPref.get_or_insert_by_user(users.get_current_user())
        if not visitor: return None
        svl = SnippetVisitLog(visitor=visitor, snippet=snippet)
        svl.put()
    
    
class SnippetVisitLog(db.Model):
    visitor = db.ReferenceProperty(UserPref)
    snippet = db.ReferenceProperty(Snippet)
    visited_at = db.DateTimeProperty(auto_now_add=True)
    
    objects = SnippetVisitLogManager()


class UserFavManager(models.Manager):
    
    def add_fav(self, user, snippet):
        snippets_count = UserFavSnippet.gql("WHERE user=:1 and snippet=:2", user, snippet).count()
        if snippets_count: return
        ufs = UserFavSnippet(user=user, snippet=snippet)
        ufs.put()
    
    def del_fav(self, user, snippet):
        snippets = UserFavSnippet.gql("WHERE user=:1 and snippet=:2", user, snippet).get()
        db.delete(snippets)
    
    def get_fav_snippets(self, user, snippet):
        snippets = UserFavSnippet.gql("WHERE user=:1 and snippet=:2").order("-inserted_at").fetch(1000)
        return snippets
        
        
class UserFavSnippet(db.Model):
    user = db.ReferenceProperty(UserPref)
    snippet = db.ReferenceProperty(Snippet)
    inserted_at = db.DateTimeProperty(auto_now_add=True)
    
    objects = UserFavManager()