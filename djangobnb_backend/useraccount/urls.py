from dj_rest_auth.registration.views import RegisterView 
from dj_rest_auth.views import LoginView,LogoutView
from django.urls import path
# from rest_framework_simplejwt.views import TokenVerifyview 
from . import api
urlpatterns=[
    path('register/',RegisterView.as_view(),name='rest_register'),
    path('login/',LoginView.as_view(),name='rest_login'),
    path('logout/',LogoutView.as_view(),name='rest_logout'),
    path("<uuid:pk>/",api.landlord_detail,name="api_landlord_detail")
]