# -*- coding: utf-8 -*-
import re
import md5
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template.context import RequestContext

from google.appengine.api import users

from snipperize.utils.webutils import signin_required
from snipperize.account.models import UserPref
from snipperize.snippet.models import Snippet
from snipperize.utils import json_response

import settings

def policy(request):
    return render_to_response('support/policy.html', context_instance=RequestContext(request))

def about(request):
    return render_to_response('support/about.html', context_instance=RequestContext(request))

def recent_updates(request):
    return render_to_response('support/recent_updates.html', context_instance=RequestContext(request))

def faq(request):
    return render_to_response('support/faq.html', context_instance=RequestContext(request))

def opensearch(request):
    response = render_to_response('support/opensearch.html', context_instance=RequestContext(request))
    response['Content-Type'] = "application/xhtml+xml; charset=utf-8"
    return response

def canvas(request):
    return render_to_response('support/canvas.html')

def rpc_relay(request):
    return render_to_response('support/rpc_relay.html')
    
def api_opensearch(request):
    if request.GET.has_key('keyword'):
        words = request.GET['keyword'].split('/')
        if len(words) > 1 and words[1] and words[0]:
            snippets = Snippet.all().filter('language', words[1]).search(words[0]).order('-published_at')
        elif len(words) > 1 and words[1]:
            snippets = Snippet.all().filter('language', words[1]).order('-published_at')
        elif words[0]:
            snippets = Snippet.all().search(words[0]).order('-published_at').fetch(50)
        else:
            snippets = Snippet.all().order('-published_at').fetch(50)

    data = []
    for s in snippets:
        tags = [t.name for t in s.get_tags()]
        data.append({'title':s.title, 'language':s.language, 'code':s.code, 'comment':s.comment, 'url':s.url, 'author':s.author.email, 'pubDate':s.published_at, 'tags':tags})
    return json_response(data)

def api_searchform(request):
    return render_to_response('support/api_searchform.html', context_instance=RequestContext(request))

@signin_required
def api_key(request):
    userPref = UserPref.get_or_insert_by_user(users.get_current_user())
    if not userPref.api_key: 
        userPref.api_key = md5.new(md5.new(str(userPref.key())).hexdigest()).hexdigest()
        userPref.put()
    return render_to_response('support/api_key.html', {'API_KEY':userPref.api_key}, context_instance=RequestContext(request))