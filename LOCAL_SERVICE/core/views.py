from django.shortcuts import render,redirect,HttpResponse
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login
# Create your views here.
def userSignupView(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        form.save()
        return redirect('login') #error
      else:
        return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request,'core/signup.html',{'form':form})

def homeView(request):
    return render(request, 'core/home.html')

def serviceListView(request):
    return render(request, 'core/service_list.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # 🔥 IMPORTANT LINE
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                if user.role == "owner":
                    return redirect('owner_dashboard')
                elif user.role == "user":
                    return redirect('user_dashboard')

            else:
                print("Authentication Failed")

        return render(request, "core/login.html", {"form": form})

    form = UserLoginForm()
    return render(request, "core/login.html", {"form": form})