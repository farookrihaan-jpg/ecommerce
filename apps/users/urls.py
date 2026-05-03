from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/',          views.RegisterView.as_view(),          name='auth-register'),
    path('login/',             views.LoginView.as_view(),             name='auth-login'),
    path('token/refresh/',     TokenRefreshView.as_view(),            name='token-refresh'),
    path('me/',                views.MeView.as_view(),                name='auth-me'),
    path('addresses/',         views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/',views.AddressDetailView.as_view(),     name='address-detail'),
]
