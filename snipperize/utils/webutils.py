# -*- coding: utf-8 -*-
import re
from django.http import HttpResponseRedirect, Http404, HttpResponse
from google.appengine.api import users
from django.core.paginator import InvalidPage, Paginator
from django.template import RequestContext, loader
from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.utils import simplejson

import settings

def signin_required(func):
    def _wrapper(request, *args, **kw):
        user = users.get_current_user()
        if user:
            return func(request, *args, **kw)
        else:
            return HttpResponseRedirect(users.create_login_url(request.get_full_path()))

    return _wrapper

def admin_required(func):
    def _wrapper(request, *args, **kw):
        if is_admin():
            return func(request, *args, **kw)
        else:
            return HttpResponseRedirect(users.create_login_url(request.get_full_path()))

    return _wrapper

def is_signin():
    user = users.get_current_user()
    if user: return True

    return False
    
def is_admin():
    user = users.get_current_user()
    if user:
        return settings.AUTHORS.count(user.email()) > 0

    return False
    
def is_ie(user_agent):
    if re.search('MSIE', user_agent): 
        return HttpResponseRedirect('/shabi.html')
    return False

class JsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(object, indent=2, cls=json.DjangoJSONEncoder, ensure_ascii=False)
        super(JsonResponse, self).__init__(content, content_type='application/json')

def safe_url(string):
    replace_req = {' ':'-', '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;', '©':'&copy;', '®':'&reg;'}
    for key, st in replace_req.items():
        string = re.sub(key, st, string)
    return string
    
def object_list(request, queryset, paginate_by=None, page=None,
        allow_empty=True, template_name=None, template_loader=loader,
        extra_context=None, context_processors=None, template_object_name='object',
        mimetype=None):
    """
    Generic list of objects.

    Templates: ``<app_label>/<model_name>_list.html``
    Context:
        object_list
            list of objects
        is_paginated
            are the results paginated?
        results_per_page
            number of objects per page (if paginated)
        has_next
            is there a next page?
        has_previous
            is there a prev page?
        page
            the current page
        next
            the next page
        previous
            the previous page
        pages
            number of pages, total
        hits
            number of objects, total
        last_on_page
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).
    """
    if paginate_by:
        paginator = Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                # Page is not 'last', nor can it be converted to an int.
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,

            # Legacy template context stuff. New templates should use page_obj
            # to access this instead.
            'is_paginated': page_obj.has_other_pages(),
            'results_per_page': paginator.per_page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_obj.number,
            'next': page_obj.next_page_number(),
            'previous': page_obj.previous_page_number(),
            'first_on_page': page_obj.start_index(),
            'last_on_page': page_obj.end_index(),
            'pages': paginator.num_pages,
            'hits': paginator.count,
            'page_range': paginator.page_range,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: queryset,
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
        }, context_processors)
        if not allow_empty and len(queryset) == 0:
            raise Http404
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    if not template_name:
        model = queryset.model
        template_name = "%s/%s_list.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(c), mimetype=mimetype)