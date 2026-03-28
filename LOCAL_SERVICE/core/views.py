from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from Accounts.models import User, Service, Booking ,ServiceProvider , Payment , Review ,Availability
import uuid
from django.core.mail import send_mail
from django.conf import settings
from .decorators import role_required
from django.contrib import messages


# User Signup View
def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            # save user properly
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # 🔥 fix
            user.save()

            send_mail(
                subject="welcome to my local_service",
                message="Thank you for registering with My Local_Service.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email]
            )

            return redirect('login')
    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})


# User Login View
def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            # 🔥 DEBUG ADD HERE
            print("EMAIL:", email)
            print("PASSWORD:", password)
            print("USER:", user)

            if user is not None:
                login(request, user)

                role = user.role.lower() if user.role else ""

                if role == "customer":
                    return redirect("customer_dashboard")
                elif role == "provider":
                    return redirect("provider_dashboard")
                else:
                    messages.error(request, "Role not defined properly.")
                    return redirect("login")

            else:
                messages.error(request, "Invalid email or password")

    else:
        form = UserLoginForm()

    return render(request, "core/login.html", {"form": form})

# Home Page
def homeView(request):
    return render(request, 'core/home.html')


# Logout
def userLogoutView(request):
    logout(request)
    return redirect('login')


@login_required
@role_required(allowed_roles=["customer"])
def customerDashboard(request):

    services = Service.objects.all()
    bookings = Booking.objects.filter(user_id=request.user.id)

    context = {
        "services": services,
        "bookings": bookings
    }

    return render(request, "core/customer_dashboard.html", context)



@login_required
@role_required(allowed_roles=["provider"])
def providerDashboard(request):

    provider = ServiceProvider.objects.first()

    services = Service.objects.filter(provider_id=provider)

    context = {
        "services": services
    }

    return render(request, "core/provider_dashboard.html", context)

@login_required
def bookService(request,service_id):

    service = Service.objects.get(id=service_id)

    if request.method == "POST":

        date = request.POST['date']
        time = request.POST['time']

        slot = Availability.objects.filter(
            provider=service.provider,
            date=date,
            start_time__lte=time,
            end_time__gte=time,
            is_available=True
        ).first()

        if slot:

            Booking.objects.create(
                user=request.user,
                provider=service.provider,
                service=service,
                booking_date=date,
                time_slot=time
            )

            slot.is_available = False
            slot.save()

            return redirect("my_bookings")

        else:

            return render(request,"book_service.html",
            {"error":"Selected time slot not available"})

    return render(request,"book_service.html")

def bookingHistory(request):
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user)
    else:
        return redirect('login')  # ya koi login url

    return render(request, 'core/history.html', {'bookings': bookings})

def acceptBooking(request,id):

    booking=Booking.objects.get(id=id)

    booking.status="Accepted"

    booking.save()

    return redirect("provider_dashboard")


def rejectBooking(request,id):

    booking=Booking.objects.get(id=id)

    booking.status="Rejected"

    booking.save()

    return redirect("provider_dashboard")

def searchService(request):

    query = request.GET.get('q')
    location = request.GET.get('location')

    services = Service.objects.all()

    if query:
        services = services.filter(service_name__icontains=query)

    if location:
        services = services.filter(provider__location__icontains=location)

    return render(request,"search.html",{"services":services})

def providerProfile(request,id):

    provider = ServiceProvider.objects.get(id=id)

    services = Service.objects.filter(provider=provider)

    return render(request,"provider_profile.html",
    {"provider":provider,"services":services})

@login_required
def myBookings(request):

    bookings = Booking.objects.filter(user=request.user)

    return render(request,"my_bookings.html",{"bookings":bookings})

@login_required
def addService(request):

    provider = ServiceProvider.objects.get(user=request.user)

    if request.method == "POST":

        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']

        Service.objects.create(

            service_name=name,
            description=description,
            price=price,
            provider=provider

        )

        return redirect("provider_dashboard")

    return render(request,"add_service.html")

def addReview(request, service_id):

    service = Service.objects.get(id=service_id)

    if request.method == "POST":

        rating = request.POST['rating']
        comment = request.POST['comment']

        Review.objects.create(
            user=request.user,
            service=service,
            rating=rating,
            comment=comment
        )

        return redirect("my_bookings")

    return render(request,"add_review.html",{"service":service})

def makePayment(request, booking_id):

    booking = Booking.objects.get(id=booking_id)

    if request.method == "POST":

        method = request.POST['payment_method']

        Payment.objects.create(
            booking = booking,
            amount = booking.service.price,
            payment_method = method,
            payment_status = "Paid",
            transaction_id = str(uuid.uuid4())
        )

        # 🔥 IMPORTANT LINE
        booking.status = "Paid"
        booking.save()

        return redirect("payment_success")

    return render(request,"payment.html",{"booking":booking})

def paymentSuccess(request):

    return render(request,"payment_success.html")

def paymentDetails(request,booking_id):

    payment = Payment.objects.get(booking_id=booking_id)

    return render(request,"payment_details.html",{"payment":payment})

@login_required
def addAvailability(request):

    provider = ServiceProvider.objects.get(user=request.user)

    if request.method == "POST":

        date = request.POST['date']
        start = request.POST['start_time']
        end = request.POST['end_time']

        Availability.objects.create(
            provider=provider,
            date=date,
            start_time=start,
            end_time=end
        )

        return redirect("provider_dashboard")

    return render(request,"add_availability.html")

def availableSlots(request,provider_id):

    slots = Availability.objects.filter(
        provider_id=provider_id,
        is_available=True
    )

    return render(request,"available_slots.html",{"slots":slots})