# -*- coding: utf-8 -*-
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

# Django settings for google-app-engine-django project.

#from config import *
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('prof.syd.xu', 'prof.syd.xu@gmail.com'),
    ('prof.syd.xu', 'thepeppersstudio@gmail.com'),
)

# users who can write blogs.
AUTHORS = ['prof.syd.xu@gmail.com']
DEFAULT_FROM_EMAIL = 'ThePeppersStudio@gmail.com'

MANAGERS = ADMINS

DATABASE_ENGINE = 'appengine'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = './media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hvhxfm5u=^*v&doo#oq8x*eg8+1&9sxbye@=umutgn^t_sg_nx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
#    'django.middleware.doc.XViewMiddleware',
     'snipperize.middleware.InfoMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
#    'django.core.context_processors.media',  # 0.97 only.
    'django.core.context_processors.request',
)

CACHE_BACKEND = "memcached:///"
CACHE_MIDDLEWARE_SECONDS=60*60

ROOT_URLCONF = 'urls'

ROOT_PATH = os.path.dirname(__file__)
#TEMPLATE_DIRS = (
#    os.path.join(ROOT_PATH, 'syd/templates'),
#)

INSTALLED_APPS = (
     'appengine_django',
     'django.contrib.auth',
     'django.contrib.markup',
     'snipperize',
     'snipperize.templatetags',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
)

TEMPLATE_DIRS = tuple([os.path.join(ROOT_PATH, app_name, 'templates') for app_name in INSTALLED_APPS])

SNIPPET_LIST_PAGE_SIZE = 10
TAG_LIST_PAGE_SIZE = 30
RELEVENT_TAG_LIMIT = 30

SITE_DOMAIN = 'http://snipperize.todayclose.com'
SITE_NAME = 'Code Snippets - Snipperize'

SUPPORT_LANGUAGES = {'pl':'Perl', 'php':'PHP', 'plain':'Plain', 'ps':'PowerShell', 'py':'Python', 'csharp': 'C#', 'cpp':'C++', 'css':'CSS', 'js':'Javascript', 'java':'Java', 'sql':'SQL', 'vb':'Visual Basic', 'xml':'XML/HTML', 'objc':'Objective-C', 'ror':'Ruby/Rails', 'as3':'ActionScript3', 'applescript':'AppleScript', 'bash':'Bash/Shell', 'coldfusion':'ColdFusion', 'delphi':'Delphi', 'diff':'Diff', 'groovy':'Groovy', 'jfx':'JavaFX', 'apache':'Apache', 'ada':'Ada', 'scala':'Scala'}

PING_LIST = ('http://blogsearch.google.com/ping/RPC2', 'http://www.feedsky.com/api/RPC2', 'http://blog.yodao.com/ping/RPC2', 'http://blog.iask.com/RPC2', 'http://www.xianguo.com/xmlrpc/ping.php', 'http://www.zhuaxia.com/rpc/server.php', 'http://api.my.yahoo.com/RPC2', 'http://rpc.technorati.com/rpc/ping', 'http://www.weblogues.com/RPC/', 'http://ping.feedburner.com/', 'http://ping.baidu.com/ping/RPC2')
