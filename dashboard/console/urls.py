from django.urls import path

from . import views

app_name = 'console'
urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_requests, name='new-logs'),
    path('processing/', views.processing_requests, name='processing-logs'),
    path('resolved/', views.resolved_requests, name='resolved-logs'),
]