"""myfirstproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path, include
from django.views.generic import RedirectView

from app.views import (
    welcome_view,
    auth_view,
    dashboard_view,
    diagnose_view,
    diagnose_result_view,
    profile_view,
    change_profile_view,
    clinic_nearby_view,
    history_view,
    logout_view,
    test,
)

urlpatterns = [
    re_path(r'^favicon\.ico$',RedirectView.as_view(url='/static/images/favicon.ico')),
    path('admin/', admin.site.urls),
    path('', welcome_view, name="welcome"),
    path('auth/', auth_view, name="auth"),
    path('dashboard/', dashboard_view, name="dashboard"),
    path('diagnose/', diagnose_view, name="diagnose"),
    path('diagnose-result/', diagnose_result_view, name="diagnose-result"),
    path('profile/', profile_view, name="profile"),
    path('change-password/', change_profile_view, name="change-password"),
    path('clinic-nearby/', clinic_nearby_view, name="clinic-nearby"),
    path('history/', history_view, name="history"),
    path('logout/', logout_view, name="logout"),
    path('test/', test, name="test"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
