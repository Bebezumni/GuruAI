# -*- encoding: utf-8 -*-

"""
Copyright (c) 2019 - present AppSeed.us
"""
from channels.layers import get_channel_layer
from main import create_msg_from_site, make_openai_request
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import ChatUser, UserMessage, AiAnswer, Company
from django.shortcuts import render
from operator import attrgetter
from itertools import chain
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from random import randint


@login_required(login_url='/login/')
def chat_view(request):
    chats = ChatUser.objects.all()
    for chat in chats:
        chat.last_message = UserMessage.objects.filter(user_id=chat.id).latest('timestamp').message_text if UserMessage.objects.filter(user_id=chat.id).exists() else None
        chat.last_ai_answer = AiAnswer.objects.filter(user_id=chat.id).latest('timestamp').message_text if AiAnswer.objects.filter(user_id=chat.id).exists() else None
        user_msgs = UserMessage.objects.filter(user_id=chat.id)
        ai_answrs = AiAnswer.objects.filter(user_id=chat.id)
        selected_user_messages = list(chain(user_msgs, ai_answrs))
        selected_user_messages.sort(key=lambda x: x.timestamp, reverse=False)
        chat.selected_user_messages = selected_user_messages
    return render(request, 'home/chat.html', {'chats': chats})

@login_required(login_url='/login/')
def company_view(request):
    company = Company.objects.first()
    return render(request, 'home/company.html', {'company': company})

@login_required(login_url='/login/')
def site_chat(request):
    if request.method == 'POST':
        print(request)
        user_id = randint(1000, 1000000)
        user_name = request.POST.get('user_name')
        user_message = request.POST.get('user_message')
        print(f'user message:  {user_message}')
        print(f"user id from site {user_id}, msg: {user_message}, name: {user_name}")
        # Simulate a response from the server
        make_openai_request(user_message, user_id, f"{user_name}(site)",)
        response_message = make_openai_request(user_message, user_id, user_name)
        # Return a JsonResponse with the response
        return JsonResponse({'status': 'success', 'response_message': response_message})


@login_required(login_url='/login/')
def site_chat_view(request):
    return render(request, 'home/chat_tilda.html')


@login_required(login_url='/login/')
def create_message_from_site(request):

    text_message = request.POST.get('text_message')

    user = request.POST.get('user')
    user_object = ChatUser.objects.get_or_create(user_id=user)
    AiAnswer.objects.create(user=user_object[0], message_text=text_message, ai_prefix='Guru: ')
    create_msg_from_site(user_object[0].messenger_id, text_message)
    return JsonResponse({'status': 'success', 'user': user, 'text_message': text_message})

@login_required(login_url='/login/')
def save_profile_info(request):
    user_name = request.POST.get('user_name')
    last_name = request.POST.get('last_name')
    e_mail = request.POST.get('e_mail')
    phone_number = request.POST.get('phone_number')
    user_id = request.POST.get('user')
    # Using get_or_create with the appropriate fields to retrieve or create the ChatUser instance
    user_object, created = ChatUser.objects.get_or_create(user_id=user_id)
    # Update the user attributes
    user_object.user_name = user_name
    user_object.last_name = last_name
    user_object.e_mail = e_mail
    user_object.phone_number = phone_number
    # Save the changes
    user_object.save()
    return JsonResponse({'status': 'success', 'user': user, 'e_mail': e_mail, 'phone_number': phone_number, 'last_name': last_name, 'user_name':user_name})

@login_required(login_url='/login/')
def chart_data(request):
    def get(self, request, *args, **kwargs):
        chats = ChatUser.objects.all()
        len_chats = len(chats)
        data = len(chats)
        return JsonResponse(list(data), safe=False)

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

