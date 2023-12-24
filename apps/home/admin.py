# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

from .models import ChatUser, UserMessage, AiAnswer, Company

admin.site.register(ChatUser)
admin.site.register(UserMessage)
admin.site.register(AiAnswer)
admin.site.register(Company)