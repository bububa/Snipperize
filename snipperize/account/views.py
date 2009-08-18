# -*- coding: utf-8 -*-
import re
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template.context import RequestContext

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
from google.appengine.ext import db

from snipperize.utils.webutils import object_list
from snipperize.utils.webutils import JsonResponse
from snipperize.account.models import UserPref
from snipperize.snippet.models import Snippet
from snipperize.snippet.models import UserFavSnippet
from snipperize.snippet.models import Tag
from snipperize.snippet.models import UserTag

import settings

def signin(request):
    if request.GET.has_key('next'):
        next = request.GET['next']
    else:
        next = '/'
    return HttpResponseRedirect(users.create_login_url(next))

def signout(request):
    return HttpResponseRedirect(users.create_logout_url('/'))

def user_language_tag_snippets(request, language, tag_name, tag_id, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    tag = Tag.get_by_id(int(tag_id))
    if not tag: raise Http404
    snippets = Tag.objects.snippets(tag)
    snippets = snippets.filter('author', user.key()).order('-published_at')
    snippets_count = snippets.count()
    snippets = snippets.filter('language', language).order('-published_at')
    rev_tags, rev_languages = get_relevent_lang_tags(user, language)
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
    
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='account/user_detail.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_snippets', 'CURRENT_LANGUAGE': current_language, 'CURRENT_TAG':tag, 'RELEVENT_TAGS': rev_tags, 'RELEVENT_LANGUAGES':rev_languages, 'CURRENT_USER_SNIPPERS_COUNT': snippets_count},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)
                
def user_tag_snippets(request, tag_name, tag_id, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    tag = Tag.get_by_id(int(tag_id))
    if not tag: raise Http404
    snippets = Tag.objects.snippets(tag)
    snippets = snippets.filter('author', user.key()).order('-published_at')
    snippets_count = Snippet.all().filter('author', user.key()).count()
    rev_tags, rev_languages = get_relevent_lang_tags(user)
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='account/user_detail.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_snippets', 'CURRENT_TAG': tag, 'RELEVENT_TAGS': rev_tags, 'RELEVENT_LANGUAGES':rev_languages, 'CURRENT_USER_SNIPPERS_COUNT': snippets_count},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def user_language_snippets(request, language, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    snippets = Snippet.all().filter('author', user.key()).order('-published_at')
    snippets_count = snippets.count()
    snippets = snippets.filter('language', language).order('-published_at')
    rev_tags, rev_languages = get_relevent_lang_tags(user, language)
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
            
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='account/user_detail.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_snippets', 'CURRENT_LANGUAGE': current_language, 'RELEVENT_TAGS': rev_tags, 'RELEVENT_LANGUAGES':rev_languages, 'CURRENT_USER_SNIPPERS_COUNT': snippets_count},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)
    
def user_detail(request, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    snippets = Snippet.all().filter('author', user.key()).order('-published_at')
    snippets_count = snippets.count()
    favs_count = UserFavSnippet.all().filter('user', user.key()).count()
    rev_tags, rev_languages = get_relevent_lang_tags(user)        
    return object_list(request, queryset=snippets, allow_empty=True,
                template_name='account/user_detail.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_snippets', 'RELEVENT_TAGS': rev_tags, 'RELEVENT_LANGUAGES':rev_languages, 'CURRENT_USER_SNIPPERS_COUNT':snippets_count, 'CURRENT_USER_FAVORITES_COUNT':favs_count},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def user_favorites(request, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    favorites = UserFavSnippet.all().filter('user', user.key()).order('-inserted_at')
    favorites_count = favorites.count()
    snippets_count = Snippet.all().filter('author', user.key()).count()
    rev_tags, rev_languages = get_relevent_lang_tags(user)        
    return object_list(request, queryset=favorites, allow_empty=True,
                template_name='account/user_favorites.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_snippets', 'RELEVENT_TAGS': rev_tags, 'RELEVENT_LANGUAGES':rev_languages, 'CURRENT_USER_SNIPPERS_COUNT':snippets_count, 'CURRENT_USER_FAVORITES_COUNT':favorites_count},
                paginate_by=settings.SNIPPET_LIST_PAGE_SIZE)

def language_tags(request, language, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    tmp_tags = UserTag.all().filter('user', user.key())
    tags = []
    for ut in tmp_tags:
        if language in ut.tag.languages: tags.append(ut.tag)
    for l, v in settings.SUPPORT_LANGUAGES.items():
        if l == language:
            current_language = {'name':v, 'key':l}
            break;
    return object_list(request, queryset=tags, allow_empty=True,
                template_name='account/tag_list.html', extra_context={'CURRENT_USER': user, 'CURRENT_LANGUAGE': current_language, 'CURRENT_PAGE': 'user_tag_list'},
                paginate_by=settings.TAG_LIST_PAGE_SIZE)
                
def tag_list(request, user_id):
    user = UserPref.get_by_id(int(user_id))
    if not user: raise Http404
    tmp_tags = UserTag.all().filter('user', user.key())
    tags = []
    for ut in tmp_tags: 
        try:
            tags.append(ut.tag)
        except:
            pass
    return object_list(request, queryset=tags, allow_empty=True,
                template_name='account/tag_list.html', extra_context={'CURRENT_USER': user, 'CURRENT_PAGE': 'user_tag_list'},
                paginate_by=settings.TAG_LIST_PAGE_SIZE)
                
def get_relevent_lang_tags(user, language=None):
    rev_tags = []
    rev_languages = []
    res = UserTag.gql("WHERE user=:1", user)
    userTags = res.fetch(settings.RELEVENT_TAG_LIMIT)
    if not userTags: return ([],[])
    for ut in userTags:
        rev_languages.extend(ut.tag.languages)
        if language == None or language in ut.tag.languages: rev_tags.append(ut.tag)
    return (rev_tags, [get_language(lang) for lang in set(rev_languages)])

def get_language(language):
    for k, v in settings.SUPPORT_LANGUAGES.items():
        if k == language: return {'name':v, 'key':k}
    return None

def add_fav_snippet(request, snippet_id):
    userPref = UserPref.get_or_insert_by_user(users.get_current_user())
    if not userPref: return JsonResponse(-1)
    snippet = Snippet.get_by_id(int(snippet_id))
    if not snippet: return JsonResponse(-2)
    UserFavSnippet.objects.add_fav(userPref, snippet)
    return JsonResponse(1)

def del_fav_snippet(request, snippet_id):
    userPref = UserPref.get_or_insert_by_user(users.get_current_user())
    if not userPref: return JsonResponse(-1)
    snippet = Snippet.get_by_id(int(snippet_id))
    if not snippet: return JsonResponse(-2)
    UserFavSnippet.objects.del_fav(userPref, snippet)
    return JsonResponse(1)