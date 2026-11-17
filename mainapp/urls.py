from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('add/', views.add_product, name='product_add'),
    path('update/<int:pk>', views.edit_product, name='product_update'),
    path('delete/<int:pk>', views.delete_product, name='product_delete'),
    path('make-bill', views.make_bill, name='make_bill'),
    path('download-bill-pdf/', views.download_bill_pdf, name='download-bill-pdf'),
    path('register-user/', views.user_registration, name='register-user'),
    path('', views.user_login, name='login-user'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('user-logout/', views.user_logout, name='user-logout'),
    path('make-inventory/', views.make_store, name='make_store'),
    path('generate-report/', views.sales_report, name='generate-report'),
    path('download-sales-report/', views.download_sales_report, name='download_sales_report'),
    path('products/search/', views.search_products, name='search-products')
]