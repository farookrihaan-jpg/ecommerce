from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def frontend(request):
    return render(request, 'index.html')

urlpatterns = [
    path('', frontend),
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/',     include('apps.users.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/cart/',     include('apps.cart.urls')),
    path('api/v1/orders/',   include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
