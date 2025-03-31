from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.api.views import SocialAuthenticationView, TestAuthView


api_router_v1 = DefaultRouter(trailing_slash=False)
api_router_v1.register("auth", SocialAuthenticationView, "social auth view")

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("auth/social/", SocialAuthenticationView.as_view(), name='social_auth'),
    path('api/test-auth/', TestAuthView.as_view(), name='test_auth'),
    path("v1/", include(api_router_v1.urls)),

]
