from django.contrib import admin
from .models import User,ServiceProvider,Admin,Category,Service,Booking,Review,Payment,Offer,Complaint,Availability

admin.site.register(User)
admin.site.register(ServiceProvider)
admin.site.register(Admin)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Offer)
admin.site.register(Complaint)
admin.site.register(Availability)
# Register your models here.
