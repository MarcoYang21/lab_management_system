# equipment/urls.py
from django.urls import path
from . import views
from .views import EquipmentListView, EquipmentDetailView, ReservationCreateView

urlpatterns = [
    path('', views.home, name='home'),
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('borrow/', views.borrow_equipment, name='borrow_equipment'),
    path('my-borrowed/', views.my_borrowed_equipment, name='my_borrowed_equipment'),
    path('equipment/<int:pk>/', EquipmentDetailView.as_view(), name='equipment_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('equipment/<int:equipment_pk>/reserve/', ReservationCreateView.as_view(), name='create_reservation'),
]
