from django.urls import path
from . import views
from .views import register,  user_login,logoutUser, client_dashboard, hm_dashboard, hm_booking, client_booking,home,register_hostel,book_room
from .views import success_booking,approve_booking,decline_booking,add_room, remove_room, hm_history


urlpatterns = [
     path('', home, name='home'),
    
    path('register/', register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', logoutUser, name="logout"),
    
    path('client_dashboard/', client_dashboard, name='client_dashboard'),
    path('hm_dashboard/', hm_dashboard, name='hm_dashboard'),
    
    path('hm_booking/', hm_booking, name='hm_booking'),
    path('client_booking/<int:hostel_id>/', client_booking, name='client_booking'),
    
    path('register_hostel/', register_hostel, name='register_hostel'),
    path('book-room/', book_room, name='book_room'),
    path('success_booking/<int:hostel_id>/', success_booking, name='success_booking'),
    
    path('approve_booking/<int:booking_id>/', approve_booking, name='approve_booking'),
    path('decline_booking/<int:booking_id>/', decline_booking, name='decline_booking'),
    
    path('update_room/<int:room_id>/', views.update_room, name='update_room'),
    path('remove_room/<int:room_id>/', views.remove_room, name='remove_room'),
    path('add_room/', views.add_room, name='add_room'),
    
    path('hm_history/', hm_history, name='hm_history'),

]
