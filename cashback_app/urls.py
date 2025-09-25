from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .auth import LoginForm

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        authentication_form=LoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/search/', views.customer_search, name='customer_search'),
    path('customers/export/', views.customer_export_csv, name='customer_export_csv'),
    
    # Purchase Management
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('purchases/create/<int:customer_id>/', views.purchase_create, name='purchase_create_for_customer'),
    
    # Admin URLs
    path('admin/operators/', views.operator_list, name='operator_list'),
    path('admin/operators/create/', views.operator_create, name='operator_create'),
    path('admin/logs/', views.activity_logs, name='activity_logs'),
    path('report/', views.reports, name='reports'),
    path('report/export/', views.report_export_csv, name='report_export_csv'),
]