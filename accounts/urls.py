from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_request, name='auth'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profile, name='profile'),
]
