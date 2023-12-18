# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import ChatUser, UserMessage, AiAnswer
from django.shortcuts import render
from operator import attrgetter

@login_required(login_url='/login/')
def chat_view(request):
    messengers = ChatUser.objects.values('messenger').distinct()
    selected_messenger = request.GET.get('messenger')
    selected_user_messages = []
    if selected_messenger:
        users = ChatUser.objects.filter(messenger=selected_messenger)
        selected_user_id = request.GET.get('user')

        if selected_user_id:
            selected_user = ChatUser.objects.get(user_id=selected_user_id)
            user_messages = UserMessage.objects.filter(user=selected_user)
            ai_messages = AiAnswer.objects.filter(user=selected_user)

            # Combine user and AI messages
            all_messages = list(user_messages) + list(ai_messages)

            # Sort messages by date
            all_messages.sort(key=lambda x: x.timestamp)

            context = {
                'messengers': messengers,
                'selected_messenger': selected_messenger,
                'users': users if selected_messenger else [],
                'selected_user_messages': all_messages if selected_user_id else [],
                'selected_user': selected_user if selected_user_id else None,
            }

            return render(request, 'home/chat.html', context)

    context = {
        'messengers': messengers,
        'selected_messenger': selected_messenger,
        'users': users if selected_messenger else [],
        'selected_user_messages': selected_user_messages,
    }

    return render(request, 'home/chat.html', context)

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

