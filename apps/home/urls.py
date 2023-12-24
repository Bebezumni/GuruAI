from django.urls import path, re_path
from apps.home import views
from .views import chat_view, create_message_from_site, company_view
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('chat', chat_view, name='chat_view'),
    path('company', company_view, name='company_view'),
    path('create_message_from_site/', create_message_from_site, name='create_message_from_site'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
