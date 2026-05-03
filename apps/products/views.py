from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer
)


class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    category  = CharFilter(field_name='category__slug')

    class Meta:
        model  = Product
        fields = ['is_featured', 'min_price', 'max_price', 'category']


# ── Categories ───────────────────────────────────────────────────────────────
class CategoryListView(generics.ListCreateAPIView):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    lookup_field       = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ── Products ─────────────────────────────────────────────────────────────────
class ProductListView(generics.ListCreateAPIView):
    queryset           = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = ProductFilter
    search_fields      = ['name', 'description', 'sku']
    ordering_fields    = ['price', 'created_at', 'name']
    ordering           = ['-created_at']

    def get_serializer_class(self):
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants', 'reviews__user')
    serializer_class = ProductDetailSerializer
    lookup_field     = 'slug'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# ── Reviews ───────────────────────────────────────────────────────────────────
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class   = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product__slug=self.kwargs['slug']).select_related('user')

    def perform_create(self, serializer):
        product = Product.objects.get(slug=self.kwargs['slug'])
        serializer.save(user=self.request.user, product=product)
