"""
URL configuration for pew project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from pew_be.views import AdminLoginAPIView, AdminRegisterAPIView, AdminLogoutAPIView, ProductAPIView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/admin/login/", AdminLoginAPIView.as_view(), name="admin-login"),

    path("api/admin/logout/", AdminLogoutAPIView.as_view(), name="admin-logout"),

    path("api/admin/register/", AdminRegisterAPIView.as_view(), name="admin-register"),

    path("api/admins/", AdminRegisterAPIView.as_view(), name="admin-list"),

    path("api/admins/<int:pk>/", AdminRegisterAPIView.as_view(), name="admin-detail"),

    path("api/products/", ProductAPIView.as_view(), name="product-list"),

    path("api/products/<int:pk>/", ProductAPIView.as_view(), name="product-detail"),
]
# =========================
# MEDIA FILES (SAFE)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)