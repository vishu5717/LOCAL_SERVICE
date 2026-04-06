from django.shortcuts import render, redirect ,HttpResponse ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from Accounts.models import User, Service, Booking ,ServiceProvider , Payment , Review ,Availability
import uuid
from django.core.mail import send_mail
from django.conf import settings
from .decorators import role_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date ,datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


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

    provider = ServiceProvider.objects.get(user=request.user)

    services = Service.objects.filter(provider_id=provider)

    context = {
        "services": services
    }

    return render(request, "core/provider_dashboard.html", context)

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
        services = services.filter(provider_id__location__icontains=location)

    return render(request,"search.html",{"services":services})

def providerProfile(request,id):

    provider = ServiceProvider.objects.get(id=id)

    services = Service.objects.filter(provider_id=provider)

    return render(request,"provider_profile.html",
    {"provider":provider,"services":services})



@login_required
def myBookings(request):

    bookings = Booking.objects.filter(user=request.user).order_by('-id')

    # 🔍 SEARCH
    query = request.GET.get('q')
    if query:
        bookings = bookings.filter(service__service_name__icontains=query)

    # 📄 PAGINATION
    paginator = Paginator(bookings, 5)
    page = request.GET.get('page')
    bookings = paginator.get_page(page)

    return render(request, "my_bookings.html", {"bookings": bookings})
@login_required
def addService(request):

    provider = ServiceProvider.objects.get(user=request.user)

    if request.method == "POST":

        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']

        Service.objects.create(
         service_name=name,
         service_description=description,
         price_range=price,
         provider_id=provider
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

    booking = get_object_or_404(Booking, id=id, user=request.user)

    if request.method == "POST":

        method = request.POST['payment_method']

        Payment.objects.create(
            booking = booking,
            amount = booking.service.price_range,
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


@login_required
@require_http_methods(["GET", "POST"])
def book_detail(request, id):

    service = get_object_or_404(Service, id=id)

    print("SERVICE:", service)
    print("PROVIDER:", service.provider_id)

    if request.method == "POST":

        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')

        # ✅ Convert string → date/time
        try:
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            selected_time = datetime.strptime(selected_time, "%H:%M").time()
        except:
            messages.error(request, "Invalid date/time ❌")
            return redirect(request.path)

        # ✅ Past date check
        if selected_date < date.today():
            messages.error(request, "Past date not allowed ❌")
            return redirect(request.path)

        # ✅ SLOT MATCH
        slot = Availability.objects.filter(
            provider=service.provider_id,
            date=selected_date,
            start_time=selected_time,
            is_available=True
        ).first()

        if not slot:
            messages.error(request, "Slot not available ❌")
            return redirect(request.path)

        # ✅ DOUBLE BOOKING CHECK
        already_booked = Booking.objects.filter(
            provider=service.provider_id,
            booking_date=selected_date,
            time_slot=selected_time
        ).exists()

        if already_booked:
            messages.error(request, "Already booked ❌")
            return redirect(request.path)

        # ✅ CREATE BOOKING
        Booking.objects.create(
            user=request.user,
            provider=service.provider_id,
            service=service,
            booking_date=selected_date,
            time_slot=selected_time,
            status="Pending"   
        )

        # ✅ UPDATE SLOT
        slot.is_available = False
        slot.save()

        messages.success(request, "Booking successful 🎉")

        return redirect("my_bookings")

    # ✅ GET REQUEST
    return render(request, "service_detail.html", {
        "service": service,
        "today": date.today()
    })
# ✅ AJAX SLOT FETCH
def get_slots_by_date(request):
    provider_id = request.GET.get('provider_id')
    selected_date = request.GET.get('date')

    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except:
        return JsonResponse({"slots": []})

    slots = Availability.objects.filter(
        provider_id=provider_id,
        date=selected_date,
        is_available=True
    ).order_by("start_time")

    data = [
        {
            "value": slot.start_time.strftime("%H:%M"),
            "label": slot.start_time.strftime("%I:%M %p")
        }
        for slot in slots
    ]

    return JsonResponse({"slots": data})

@login_required
def cancel_booking(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)

    slot = Availability.objects.filter(
        provider=booking.provider_id,
        date=booking.booking_date,
        start_time=booking.time_slot
    ).first()

    if slot:
        slot.is_available = True
        slot.save()

    booking.delete()

    messages.success(request, "Booking cancelled ✅")

    return redirect("my_bookings")