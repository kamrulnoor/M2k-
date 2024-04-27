"""
URL configuration for webpage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
import webpage.views as views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("options.html", views.options, name="options"),
    path("researchers-login.html", views.rlogin, name="rlogin"),
    path("labelers-login.html", views.llogin, name="llogin"),
    path("labelers dashboard.html", views.ldashboard, name="ldashboard"),
    path("old dash.html", views.rdashboard, name="rdashboard"),
    path("researchers dashboard.html", views.rdashboard, name="rdashboard"),
    path("download-data.html", views.download_data, name="download_data"),
    path("landingpage.html", views.landing, name="landing"),
    path("researchers data.html", views.rdata, name="rdata"),
    path("upload-data.html", views.udata, name="udata"),
    path("foods.html", views.fooddata, name="fooddata"),
    path("labels.html", views.labeldata, name="labeldata"),
    path("marketing.html", views.marketdata, name="marketdata"),
    path("technique.html", views.techdata, name="techdata"),
    path("healthy.html", views.healthdata, name="healthdata")
]
