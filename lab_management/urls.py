"""
URL configuration for lab_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# project/urls.py
from django.urls import path, include
from equipment.admin import admin_site

urlpatterns = [
    path('', include('equipment.urls')),  # 這會包含首頁和其他 equipment 應用的 URL
    path('admin/', admin_site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # 用於處理登入、登出等
]
