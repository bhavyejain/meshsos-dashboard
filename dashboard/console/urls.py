from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'console'
urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/console/'), name='logout'),
    path('all/', views.index, name='index'),
    path('new/', views.new_requests, name='new-logs'),
    path('processing/', views.processing_requests, name='processing-logs'),
    path('resolved/', views.resolved_requests, name='resolved-logs'),
    path('detail/<int:pk>/', views.request_detail, name='details'),
    path('update_status/<int:pk>/<str:status>/', views.update_status, name='update-status'),
    path('profile/', views.profile, name='profile'),
]