# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *
from django.conf import settings
from snipperize.snippet import views as snippet_views
from snipperize.account import views as account_views
from snipperize.support import views as support_views
from snipperize.feeds import views as feed_views
from snipperize.feeds.models import LatestSnippets
from snipperize.feeds.models import UserSnippets
from snipperize.feeds.models import LanguageSnippets
from snipperize.feeds.models import TagSnippets
from snipperize.feeds.models import LanguageTagSnippets

feeds = {
    'latest': LatestSnippets,
    'user': UserSnippets,
    'language': LanguageSnippets,
    'tag': TagSnippets,
    'language_tag':LanguageTagSnippets,
}

urlpatterns = patterns('',
    # Example:
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    #(r'^about/$', 'syd.blog.views.about'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^tasks/update_tag_correlations/(?P<offset>\d+)/$', 'snipperize.task.views.update_tag_correlations')
    #url (r'^canvas.html$', blog_views.canvas, name='canvas'),
    #url (r'^rpc_relay.html$', blog_views.rpc_relay, name='rpc_relay'),
    # Uncomment this for admin:
    #(r'^admin/', include('django.contrib.admin.urls')),
)

urlpatterns += patterns('',
    url (r'^api/key/$',
        view=support_views.api_key,
        name='api_key'
        ),
    url (r'^sitemap/$', 
        view=snippet_views.sitemap, 
        name='sitemap'
        ),
    url (r'^rss/lastest/$',
        view=feed_views.latest_feed_proxy,
        name='rss_latest'
        ),
    url (r'^ajax/user_fav_snippet/delete/(?P<snippet_id>\d+)/$',
        view=account_views.del_fav_snippet,
        name='del_fav_snippet'
        ),
    url (r'^ajax/user_fav_snippet/add/(?P<snippet_id>\d+)/$',
        view=account_views.add_fav_snippet,
        name='add_fav_snippet'
        ),
    url (r'^api/searchform/$',
        view=support_views.api_searchform,
        name='api_searchform'
        ),
    url (r'^api/opensearch/$',
        view=support_views.api_opensearch,
        name='api_opensearch'
        ),
    url (r'^opensearch/$',
        view=support_views.opensearch,
        name='opensearch'
        ),
    url (r'^faq/$',
        view=support_views.faq,
        name='faq'
        ),
    url (r'^recent-updates/$',
        view=support_views.recent_updates,
        name='recent_updates'
        ),
    url (r'^about/$',
        view=support_views.about,
        name='about'
        ),
    url (r'^privacy/$',
        view=support_views.policy,
        name='policy'
        ),
    url (r'^signin/$',
        view=account_views.signin,
        name='signin'
        ),
    url (r'^signout/$',
        view=account_views.signout,
        name='signout'
        ),
    url (r'^user/favorites/(?P<user_id>\d+)/$',
        view=account_views.user_favorites,
        name='user_favorites'
        ),
    url (r'^user/snippets/(?P<user_id>\d+)/$',
        view=account_views.user_detail,
        name='user_detail'
        ),
    url (r'^users/tags/(?P<language>[-\w]+)/(?P<user_id>\d+)/$',
        view=account_views.language_tags,
        name='user_language_tags'),
    url (r'^users/tags/(?P<user_id>\d+)/$',
        view=account_views.tag_list,
        name='user_tag_list'),
    url (r'^user/(?P<tag_name>[-\w]+)--(?P<tag_id>[-\w]+)/(?P<user_id>\d+)/$',
        view=account_views.user_tag_snippets,
        name='user_tag_snippets'
        ),
    url (r'^user/(?P<language>[-\w]+)/(?P<user_id>\d+)/$',
        view=account_views.user_language_snippets,
        name='user_language_snippets'
        ),
    url (r'^user/(?P<language>[-\w]+)/(?P<tag_name>[-\w]+)--(?P<tag_id>[-\w]+)/(?P<user_id>\d+)/$',
        view=account_views.user_language_tag_snippets,
        name='user_language_tag_snippets'
        ),
    url (r'^languagess/$',
        view=snippet_views.language_list,
        name='language_list'),
    url (r'^tags/(?P<language>[-\w]+)/$',
        view=snippet_views.language_tags,
        name='language_tags'),
    url (r'^tags/$',
        view=snippet_views.tag_list,
        name='tag_list'),
    url (r'^snippet/add/$',
        view=snippet_views.snippet_add,
        name='snippet_add'),
    url (r'^snippet/edit/(?P<snippet_id>\d+)/$',
        view=snippet_views.snippet_edit,
        name='snippet_edit'),
    url (r'^snippet/delete/(?P<snippet_id>\d+)/$',
        view=snippet_views.snippet_delete,
        name='snippet_delete'),
    url (r'^snippets/$',
        view=snippet_views.snippet_search,
        name='snippet_search'),
    url (r'^snippets/sitemap/$',
        view=snippet_views.snippet_sitemap,
        name='snippet_sitemap',
        ),
    url (r'^snippets/(?P<tag_name>[-\w]+)--(?P<tag_id>\d+)/$',
        view=snippet_views.tag_snippets,
        name='tag_snippets'),
    url (r'^snippets/(?P<language>[-\w]+)/$',
        view=snippet_views.language_snippets,
        name='language_snippets'),
    url (r'^snippets/(?P<language>[-\w]+)/(?P<tag_name>[-\w]+)--(?P<tag_id>\d+)/$',
        view=snippet_views.language_tag_snippets,
        name='language_tag_snippets'),
    url (r'^version/(?P<snippet_language>[-\w]+)/(?P<snippet_title>[^^]*?)--(?P<snippet_id>\d+)--(?P<subversion_id>\d+)/$',
        view=snippet_views.subversion_detail,
        name='snippet_subversion_detail'),
    url (r'^snippet/(?P<snippet_language>[-\w]+)/(?P<snippet_title>[^^]*?)--(?P<snippet_id>\d+)/$',
        view=snippet_views.snippet_detail,
        name='snippet_detail'),
    url(r'^$',
        view=snippet_views.snippet_list,
        name='index'),
)

