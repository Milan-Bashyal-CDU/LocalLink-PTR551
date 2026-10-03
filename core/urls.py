from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/offer/', views.offer_create, name='offer_create'),
    path('requests/<int:pk>/complete/', views.request_complete, name='request_complete'),
    path('requests/<int:pk>/cancel/', views.request_cancel, name='request_cancel'),
    path('requests/<int:pk>/review/', views.review_create, name='review_create'),
    path('requests/<int:pk>/message/', views.message_create, name='message_create'),
    path('offers/<int:pk>/accept/', views.offer_accept, name='offer_accept'),
]
