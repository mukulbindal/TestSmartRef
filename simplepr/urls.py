"""simplepr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)
from restorent.views import home,about,postenter,ShowCurrentInventory,login,postlogin,postsignup,signup,logout
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'^favicon\.ico$', favicon_view),
    path('',home),
    path('home/',home),
    path('about/',about),
    path('postenter/',postenter),
    path('ShowCurrentInventory/',ShowCurrentInventory),
    path('login/',login),
    path('postlogin/',postlogin),
    path('signup/',signup),
    path('postsignup/',postsignup),
    path('logout/',logout)
]
