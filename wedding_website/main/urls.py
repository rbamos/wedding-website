# main/urls.py
from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('password_reset/', password_reset_view, name='password_reset'), # TODO
    path('qr/<slug:auth_token>/', qr_signin, name='qr_signin'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('settings/', settings_view, name='settings'),
    path(
        'password_change/', 
        auth_views.PasswordChangeView.as_view(template_name="registration/password_change.html"), 
        name='password_change'
    ),
    path(
        'password_change_done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'), 
        name='password_change_done'
    ),
    path('guest_list/', guest_list, name='guest_list'),
    path('rsvp/', rsvp_view, name='rsvp'),
    path('gallery/', gallery_view, name='gallery'),
    path('hotels/', hotel_view, name='hotels'),
    path('schedule/', schedule_view, name='schedule'),
    path('faq/', faq_view, name='faq'),
    path('registry/', registry_view, name='registry'),
]
