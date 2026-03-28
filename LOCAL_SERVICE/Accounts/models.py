from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # VERY IMPORTANT
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **extra_fields)

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    address = models.TextField()
    

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "User"

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, null=True, blank=True)
    service_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    experience = models.IntegerField()
    availability = models.BooleanField(default=True)

    class Meta:
        db_table = "ServiceProvider"

    def __str__(self):
        return self.name


class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=50)

    class Meta:
        db_table = "Admin"

    def __str__(self):
        return self.name


class Category(models.Model):
    categoryName = models.CharField(max_length=100)
    categoryDescription = models.TextField()
    categoryStatus = models.BooleanField(default=True)

    class Meta:
        db_table = "Category"

    def __str__(self):
        return self.categoryName


class Service(models.Model):
        service_name = models.CharField(max_length=100)
        service_description = models.TextField(null=True)
        price_range = models.IntegerField(null=True)
        availability_status = models.BooleanField(default=True)
        created_at = models.DateTimeField(default=timezone.now)

        category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
        provider_id = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, null=True)

        image = models.ImageField(upload_to="services/", null=True, blank=True)

        class Meta:
            db_table = "Service"

        def __str__(self):
            return self.service_name


class Booking(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE,null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True)

    booking_date = models.DateField()
    time_slot = models.TimeField()

    booking_status = models.BooleanField(default=False)

    address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Booking"

    def __str__(self):
        return f"{self.user} - {self.service}"

class Review(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True)

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    


class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('NET', 'Net Banking'),
        ('WALLET', 'Wallet'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    payment_status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)


    payment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Payment"


class Offer(models.Model):
    coupon_code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "Offer"


class Complaint(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)

    issue_text = models.TextField()
    status = models.CharField(max_length=50)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Complaint"

class Availability(models.Model):

    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name="provider_slots"
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "Availability"

    def __str__(self):
        return f"{self.provider} - {self.date}"



