from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.ProductListView.as_view(),       name='product-list'),
    path('categories/',                   views.CategoryListView.as_view(),      name='category-list'),
    path('categories/<slug:slug>/',       views.CategoryDetailView.as_view(),    name='category-detail'),
    path('<slug:slug>/',                  views.ProductDetailView.as_view(),     name='product-detail'),
    path('<slug:slug>/reviews/',          views.ReviewListCreateView.as_view(),  name='product-reviews'),
]