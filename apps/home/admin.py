# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

from .models import ChatMessage, ChatUser, UserMessage, AiAnswer

admin.site.register(ChatMessage)
admin.site.register(ChatUser)
admin.site.register(UserMessage)
admin.site.register(AiAnswer)
