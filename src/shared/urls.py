"""
URL configuration for shared project.

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
from ninja import NinjaAPI
from user.authentication import bearer_auth
from user.exceptions import NotAuthorizedException, UserNotFoundException

base_api = NinjaAPI(title="Goodpang", version="0.0.0")


@base_api.get("")
def health_check_handler(request):
    return {"ping": "pong"}


@base_api.get("/auth-test", auth=bearer_auth)
def auth_test(request):
    return {
        "token": request.auth,
        "email": request.user.email,
    }


@base_api.exception_handler(NotAuthorizedException)
def not_authorized_exception(request, exc):
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )


@base_api.exception_handler(UserNotFoundException)
def user_not_found_exception(request, exc):
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=404,
    )


urlpatterns = [
    path("", base_api.urls),
    path("admin/", admin.site.urls),
]
