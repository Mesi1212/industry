import datetime
import json
import os

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from start.models import CustomUser, Staff, Student


from start.EmailBackEnd import EmailBackEnd
from start.models import CustomUser, Courses, SessionYearModel
from student import settings


def showDemoPage(request):
    return render(request,"demo.html")

def ShowLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = CustomUser.objects.filter(email=email).first()

        if user is not None and user.check_password(password):
            login(request, user)
            if user.user_type == 1:
                return HttpResponseRedirect('/admin_home')
            elif user.user_type == 2:
                return HttpResponseRedirect(reverse("staff_home"))
            else:
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")

def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
         '        apiKey: "YOUR_API_KEY",' \
         '        authDomain: "FIREBASE_AUTH_URL",' \
         '        databaseURL: "FIREBASE_DATABASE_URL",' \
         '        projectId: "FIREBASE_PROJECT_ID",' \
         '        storageBucket: "FIREBASE_STORAGE_BUCKET_URL",' \
         '        messagingSenderId: "FIREBASE_SENDER_ID",' \
         '        appId: "FIREBASE_APP_ID",' \
         '        measurementId: "FIREBASE_MEASUREMENT_ID"' \
         ' };' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'

    return HttpResponse(data,content_type="text/javascript")

def Testurl(request):
    return HttpResponse("Ok")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def signup_student(request):
    courses=Courses.objects.all()
    session_years=SessionYearModel.objects.all()
    return render(request,"signup_student_page.html",{"courses":courses,"session_years":session_years})

def signup_staff(request):
    return render(request,"signup_staff_page.html")

def do_admin_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))

def do_signup_staff(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")

        # Validate form data
        if not all([username, email, password, address]):
            messages.error(request, "All fields are required")
            return render(request, "signup_staff_page.html")

        try:
            # Create or update user
            user, created = CustomUser.objects.update_or_create(
                username=username,
                email=email,
                defaults={"password": password, "user_type": 2}
            )

            # Create or update staff profile
            staff, created = Staff.objects.update_or_create(
                admin=user,
                defaults={"address": address}
            )

            messages.success(request, "Successfully Created Staff")
            return HttpResponseRedirect(reverse("show_login"))
        except Exception as e:
            messages.error(request, f"Failed to Create Staff: {e}")

    return render(request, "signup_staff_page.html")


from django.core.exceptions import ObjectDoesNotExist

def do_signup_student(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        session_year_id = request.POST.get("session_year")
        course_id = request.POST.get("course")
        sex = request.POST.get("sex")
        # Validate form data
        if not all([first_name, last_name, username, email, password, address, session_year_id, course_id, sex]):
            messages.error(request, "All fields are required")
            return render(request, "signup_student_page.html", {"courses": Courses.objects.all(), "session_years": SessionYearModel.objects.all()})

        try:
            # Create or update user
            user, created = CustomUser.objects.update_or_create(
                email=email,
                defaults={"username": username, "password": password, "first_name": first_name, "last_name": last_name, "user_type": 3}
            )

            # Create or update student profile
            student, created = Student.objects.update_or_create(
                admin=user,
                defaults={"gender": sex, "address": address, "course": Courses.objects.get(id=course_id), "session_start_year": SessionYearModel.objects.get(id=session_year_id).session_start_year, "session_end_year": SessionYearModel.objects.get(id=session_year_id).session_end_year}
            )

            messages.success(request, "Successfully Added Student")
            return HttpResponseRedirect(reverse("show_login"))
        except Exception as e:
            messages.error(request, f"Failed to add student: {e}")

    return render(request, "signup_student_page.html", {"courses": Courses.objects.all(), "session_years": SessionYearModel.objects.all()})
