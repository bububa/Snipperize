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
from google.appengine.api import images

from snipperize.utils.webutils import signin_required
from snipperize.utils.webutils import admin_required
from snipperize.utils.webutils import is_admin
from snipperize.utils.webutils import is_signin
from snipperize.utils.webutils import object_list
from snipperize.utils.GAEXMLRPCTransport import ping

from snipperize.snippet.models import Snippet
from snipperize.snippet.forms import SnippetForm
from snipperize.snippet.models import Tag
from snipperize.task.models import TagCoef
from snipperize.snippet.models import Subversion

from snipperize.snippet.models import SnippetVisitLogManager

import settings

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
        
@signin_required
def snippet_add(request, profile_callback=None):
    if request.method == 'GET':
        form = SnippetForm()
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        logging.getLogger().debug(form)
        if form.is_valid():
            new_snippet = form.save(profile_callback=profile_callback)
            memcache.flush_all()
            ping()
            return HttpResponseRedirect('/')

    return render_to_response('snippet/snippet_add.html', {'form': form, 'CURRENT_PAGE':'snippet_add'}, context_instance=RequestContext(request))

@signin_required
def snippet_edit(request, snippet_id, profile_callback=None):
    snippet = Snippet.get_by_id(int(snippet_id))
    if not snippet: raise Http404
    
    if request.method == 'GET':
        tags = ''
        if snippet.tags: tags = ','.join([t.name for t in snippet.get_tags() if t])
        form = SnippetForm({'title': snippet.title,
                        'language': snippet.language,
                        'code': snippet.code,
                        'url': snippet.url,
                        'comment': snippet.comment,
                        'private': snippet.private,
                        'tag': tags})
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        logging.getLogger().debug(form)
        if form.is_valid():
            updated_snippet = form.edit(int(snippet_id), profile_callback=profile_callback)
            memcache.flush_all()
            ping()
            return HttpResponseRedirect(updated_snippet.get_absolute_url())

    return render_to_response('snippet/snippet_edit.html', {'form': form, 'snippet': snippet}, context_instance=RequestContext(request))

@signin_required
def snippet_delete(request, snippet_id, profile_callback=None):
    language = Snippet.objects.delete_snippet(int(snippet_id))
    if not language: raise Http404
    memcache.flush_all()
    return HttpResponseRedirect('/snippets/%s/'%language)

def snippet_detail(request, snippet_id, snippet_language, snippet_title):
    snippet = Snippet.get_by_id(int(snippet_id))
    if not snippet: raise Http404
    svlm = SnippetVisitLogManager()
    svlm.log(snippet)
    if request.method == 'POST':
        snippet.add_comment(request.POST['commentContent'])
    memcache.flush_all()
    subversions = snippet.get_subversions()
    comments = snippet.get_comments()
    return render_to_response('snippet/snippet_detail.html', {'snippet':snippet, 'subversions':subversions, 'comments':comments}, context_instance=RequestContext(request))

def subversion_detail(request, subversion_id, snippet_id, snippet_language, snippet_title):
    subversion = Subversion.get_by_id(int(subversion_id))
    if not subversion: raise Http404
    if request.method == 'POST':
        subversion.add_comment(request.POST['commentContent'])
    memcache.flush_all()
    comments = subversion.get_comments()
    return render_to_response('snippet/subversion_detail.html', {'subversion':subversion, 'comments':comments}, context_instance=RequestContext(request))
   
def language_snippets(request, language):
    snippets = Snippet.all().filter('language', language).order('-published_at')
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
    rev_tags = Tag.all().filter('languages', language).order('-number').order('-inserted_at').fetch(settings.RELEVENT_TAG_LIMIT)
           
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='snippet/snippet_list.html', extra_context={'CURRENT_LANGUAGE': current_language, 'CURRENT_PAGE': 'snippet_list', 'RELEVENT_TAGS':rev_tags},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def language_tag_snippets(request, language, tag_name, tag_id):
    tag = Tag.get_by_id(int(tag_id))
    if not tag: raise Http404
    rev = TagCoef.all().filter('tag',tag.key()).order('distance').fetch(settings.RELEVENT_TAG_LIMIT)
    rev_tags = []
    if rev: rev_tags = [rt.related_tag for rt in rev if language in rt.related_tag.languages]
    else: rev_tags = Tag.all().filter('languages', language).order('-number').order('-inserted_at').fetch(settings.RELEVENT_TAG_LIMIT)
    
    snippets = Tag.objects.snippets(tag)
    snippets = snippets.filter('language', language).order('-published_at')
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
            
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='snippet/snippet_list.html', extra_context={'CURRENT_LANGUAGE': current_language, 'CURRENT_TAG':tag, 'CURRENT_PAGE': 'snippet_list', 'RELEVENT_TAGS':rev_tags},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def tag_snippets(request, tag_name, tag_id):
    tag = Tag.get_by_id(int(tag_id))
    if not tag: raise Http404
    rev = TagCoef.all().filter('tag',tag.key()).order('distance').fetch(settings.RELEVENT_TAG_LIMIT)
    rev_tags = []
    if rev: rev_tags = [rt.related_tag for rt in rev]
    else: rev_tags = Tag.all().order('-number').order('-inserted_at').fetch(settings.RELEVENT_TAG_LIMIT)
    
    snippets = Tag.objects.snippets(tag)
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='snippet/snippet_list.html', extra_context={'CURRENT_TAG':tag, 'CURRENT_PAGE': 'snippet_list', 'RELEVENT_TAGS':rev_tags},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def snippet_search(request):
    if request.GET.has_key('keyword'):
        keyword = request.GET['keyword']
        logging.getLogger().info(keyword)
        if request.GET.has_key('search_language') and request.GET['search_language']:
            snippets = Snippet.all().filter('language', request.GET['search_language']).search(keyword).order('-published_at')
        else:
            snippets = Snippet.all().search(keyword).order('-published_at')
    else:
        if request.GET.has_key('search_language') and request.GET['search_language']:
            snippets = Snippet.all().filter('language', request.GET['search_language']).order('-published_at')
        else:
            snippets = Snippet.all().order('-published_at')
    rev_tags = Tag.all().order('-number').order('-inserted_at').fetch(settings.RELEVENT_TAG_LIMIT)
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='snippet/snippet_list.html', extra_context={'is_admin': is_admin(), 'CURRENT_PAGE': 'snippet_list', 'RELEVENT_TAGS':rev_tags},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)
           
def snippet_list(request):
    snippets = Snippet.all().order('-published_at')
    
    rev_tags = Tag.all().order('-number').order('-inserted_at').fetch(settings.RELEVENT_TAG_LIMIT)
    
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='snippet/snippet_list.html', extra_context={'is_admin': is_admin(), 'CURRENT_PAGE': 'snippet_list', 'RELEVENT_TAGS':rev_tags},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def language_tags(request, language):
    tags = Tag.all().filter('languages', language).order('-number').order('-inserted_at')
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
    return object_list(request, queryset=tags, allow_empty=True,
                template_name='snippet/tag_list.html', extra_context={'CURRENT_LANGUAGE': current_language, 'CURRENT_PAGE': 'tag_list'},
                paginate_by=settings.TAG_LIST_PAGE_SIZE)
                
def tag_list(request):
    tags = Tag.all().order('-number').order('-inserted_at')
    return object_list(request, queryset=tags, allow_empty=True,
                template_name='snippet/tag_list.html', extra_context={'CURRENT_PAGE': 'tag_list'},
                paginate_by=settings.TAG_LIST_PAGE_SIZE)

def language_list(request):
    languages = []
    for alias, lang in settings.SUPPORT_LANGUAGES.items():
        tags = Tag.all().filter('languages', alias).order('-number').order('-inserted_at')
        languages.append({'alias':alias, 'lang':lang, 'tags':tags.fetch(10)})
    return render_to_response('snippet/snippet_sitemap.html', {'SUPPORT_LANGUAGES': languages, 'CURRENT_PAGE':'language_list'}, context_instance=RequestContext(request))
    
def snippet_sitemap(request):
    languages = []
    for alias, lang in settings.SUPPORT_LANGUAGES.items():
        tags = Tag.all().filter('languages', alias).order('-number').order('-inserted_at')
        if not tags.count():continue
        languages.append({'alias':alias, 'lang':lang, 'tags':tags.fetch(10)})
    return render_to_response('snippet/snippet_sitemap.html', {'SUPPORT_LANGUAGES': languages}, context_instance=RequestContext(request))
    
def sitemap(request):
    str = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.google.com/schemas/sitemap/0.84" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.google.com/schemas/sitemap/0.84 http://www.google.com/schemas/sitemap/0.84/sitemap.xsd">
            <url>
                <loc>%s/</loc>
                <changefreq>daily</changefreq>
                <priority>0.9</priority>
            </url>
        '''%settings.SITE_DOMAIN
    
    for alias, lang in settings.SUPPORT_LANGUAGES.items():
        str += '''<url>
                    <loc>%s%s</loc>
                      <changefreq>daily</changefreq>
                      <priority>0.8</priority>
                   </url>
                '''%(settings.SITE_DOMAIN, reverse('language_snippets', kwargs={'language':alias}))
    for tag in Tag.all():
        str += '''<url>
                    <loc>%s%s</loc>
                      <changefreq>daily</changefreq>
                      <priority>0.8</priority>
                   </url>
                '''%(settings.SITE_DOMAIN, reverse('tag_snippets', kwargs={'tag_name':tag.get_escape_name(), 'tag_id':tag.key().id()}))
    
    for alias, lang in settings.SUPPORT_LANGUAGES.items():
        tags = Tag.all().filter('languages', alias)
        if not tags: continue
        for tag in tags:
            str += '''<url>
                        <loc>%s%s</loc>
                          <changefreq>daily</changefreq>
                          <priority>0.8</priority>
                       </url>
                    '''%(settings.SITE_DOMAIN, reverse('language_tag_snippets', kwargs={'language':alias, 'tag_name':tag.get_escape_name(), 'tag_id':tag.key().id()}))
    
    for snippet in Snippet.all():
        str += '''<url>
                    <loc>%s%s</loc>
                    <changefreq>monthly</changefreq>
                    <priority>0.5</priority>
                </url>
                '''%(settings.SITE_DOMAIN, snippet.get_absolute_url())
    
    str += '</urlset>'
    return HttpResponse(str, content_type='text/xml')