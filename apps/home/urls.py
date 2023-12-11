# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import chat_view
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('chat', chat_view, name='chat_view'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
