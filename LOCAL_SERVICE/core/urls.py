from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    
    path('signup/',views.userSignupView,name='signup'),
    path('', views.homeView, name='home'),
 
    path('login/',views.userLoginView,name='login'),
    path('logout/', views.userLogoutView, name='logout'),
    
    path('provider-dashboard/', views.providerDashboard, name='provider_dashboard'),
    path('customer-dashboard/', views.customerDashboard, name='customer_dashboard'),
    
    


    path("accept/<int:id>/",views.acceptBooking,name="accept_booking"),

    path("reject/<int:id>/",views.rejectBooking,name="reject_booking"),

    path("search/",views.searchService,name="search"),

    path('provider/<int:id>/',views.providerProfile,name="provider_profile"),
    
    
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('cancel-booking/<int:id>/', views.cancel_booking, name='cancel_booking'),
    path('history/',views.bookingHistory,name="booking_history"),
    
    
    path("my-bookings/",views.myBookings,name="my_bookings"),
    path('get-slots/', views.get_slots_by_date, name='get_slots'),

    path("add-service/",views.addService,name="add_service"),

    path("payment/<int:booking_id>/",views.makePayment,name="make_payment"),

    path("payment-success/",views.paymentSuccess,name="payment_success"),

    path("payment-details/<int:booking_id>/",views.paymentDetails,name="payment_details"),

    path("add-availability/",views.addAvailability,name="add_availability"),

]