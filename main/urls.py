from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('api/visitor-count/', views.get_visitor_count, name='visitor-count'),
    path('products/<str:product_category>/<slug:product_slug>/', views.product_details, name='product-detail'),
    path('products/<str:product_category>', views.products_list, name='products-list'),
    path('payment', views.buy),
    path('search/', views.search, name='search')
]