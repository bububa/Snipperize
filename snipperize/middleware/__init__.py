import datetime
import time
import re

from urlparse import urlparse
from django.core.urlresolvers import resolve
from google.appengine.api import users
from snipperize.account.models import UserPref
from snipperize.utils.webutils import is_admin
import sys
import settings

class InfoMiddleware(object):

    def process_request(self, request):
    
        request.SUPPORT_LANGUAGES = settings.SUPPORT_LANGUAGES
        request.SITE_NAME = settings.SITE_NAME
        request.SITE_DOMAIN = settings.SITE_DOMAIN
        request.IS_ADMIN = is_admin()
        
        
        current_user = users.get_current_user()
        if current_user:
            request.current_user = UserPref.get_or_insert_by_user(current_user)
        return None
