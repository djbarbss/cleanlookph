from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("home")  # change this to your page
        else:
            return render(request, "authentication/login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "authentication/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

def register_view(request):
    if request.method == "POST":
        User = get_user_model()
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        birthday = request.POST.get("birthday")
        password = request.POST.get("password")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.birthday = birthday
        user.save()

        return redirect("home")

    return render(request, "authentication/register.html")

@login_required
def profile_view(request):
    return render(request, "authentication/profile.html")