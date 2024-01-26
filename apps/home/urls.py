from django.urls import path, re_path
from apps.home import views
from .views import chat_view, create_message_from_site, company_view, site_chat_view, site_chat, token_view, template_send, chatapp_webhook
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('chat', chat_view, name='chat_view'),
    path('company', company_view, name='company_view'),
    path('create_message_from_site/', create_message_from_site, name='create_message_from_site'),
    path('site_chat/', site_chat, name='site_chat'),
    path('site_chat_view', site_chat_view, name='site_chat_view'),
    path('token_view/', token_view, name='token_view'),
    path('template_send/<str:phone>/<str:name>/', template_send, name='template_send'),
    path('chatapp_webhook/', chatapp_webhook, name='chatapp_webhook'),
    re_path(r'^.*\.*', views.pages, name='pages'),
    


]
