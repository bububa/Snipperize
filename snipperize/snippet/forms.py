# -*- coding: utf-8 -*-
import sys
from google.appengine.ext.db import djangoforms as forms
from snipperize.snippet.models import Snippet
from django import forms

import settings

required_attrs_dict = { 'class': 'required' }

class SnippetForm(forms.ModelForm):
    languages = settings.SUPPORT_LANGUAGES
    title = forms.CharField(label=u'Title', widget=forms.TextInput(attrs=required_attrs_dict), required=True)
    code = forms.CharField(label=u'Code', widget=forms.Textarea(attrs=required_attrs_dict), required=True)
    comment = forms.CharField(label=u'Comment', widget=forms.Textarea(), required=False)
    url = forms.URLField(label=u'URL', widget=forms.TextInput(), required=False)
    language = forms.ChoiceField(label=u'Language', choices = ((a, l) for a,l in settings.SUPPORT_LANGUAGES.items()), required=True)
    tag = forms.CharField(label=u'Tag', widget=forms.TextInput(attrs=required_attrs_dict), required=True)
    private = forms.BooleanField(label=u'Private', required=False)
    class Meta:
        model = Snippet
        exclude = ['author', 'tags']
    
    def save(self, profile_callback=None):
        new_snippet = Snippet.objects.add_snippet(title=self.cleaned_data['title'],
                                            code=self.cleaned_data['code'],
                                            comment=self.cleaned_data['comment'],
                                            language=self.cleaned_data['language'],
                                            url=self.cleaned_data['url'],
                                            tags=self.cleaned_data['tag'],
                                            private=self.cleaned_data['private'],
                                            profile_callback=profile_callback)
        return new_snippet
    
    def edit(self, snippet_id, profile_callback=None):
        updated_snippet = Snippet.objects.edit_snippet(snippet_id=snippet_id,
                                            title=self.cleaned_data['title'],
                                            code=self.cleaned_data['code'],
                                            comment=self.cleaned_data['comment'],
                                            language=self.cleaned_data['language'],
                                            url=self.cleaned_data['url'],
                                            tags=self.cleaned_data['tag'],
                                            private=self.cleaned_data['private'],
                                            profile_callback=profile_callback)
        return updated_snippet