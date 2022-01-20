import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File

from app.forms import RegistrationForm, AccountAuthenticationForm
from app.models import Account, get_coughing_audio_filepath
from app.forms import AudioForm

from .knn.core import main

def welcome_view(request):
    context = {}
    return render(request, 'welcome.html', context)

def auth_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated: 
        return redirect("dashboard")
    destination = get_redirect_if_exists(request)
    print("destination: " + str(destination))
    
    context = {}
    
    # login
    if 'login-btn' in request.POST:
        if request.POST:
            form = AccountAuthenticationForm(request.POST)
            if form.is_valid():
                email = request.POST['email']
                password = request.POST['password']
                user = authenticate(email=email, password=password)
                if user:
                    login(request, user)
                    if destination:
                        return redirect(destination)
                    return redirect("dashboard")

        else:
            form = AccountAuthenticationForm()

        context['login_form'] = form
    
    # register
    elif 'register-btn' in request.POST:
        if request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                # email = form.cleaned_data.get('email').lower()
                # raw_password = form.cleaned_data.get('password1')
                # account = authenticate(email=email, password=raw_password)
                # login(request, account)
                destination = kwargs.get("next")
                if destination:
                    return redirect(destination)
                return redirect('welcome')
            else:
                context['registration_form'] = form

        else:
            form = RegistrationForm()
            context['registration_form'] = form
        
    return render(request, "auth.html", context)

def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect

# def menu_view(request, *args, **kwargs):
#     context = {}
    # user_id = kwargs.get("user_id")
    # try:
    #     account = Account.objects.get(pk=user_id)
    # except:
    #     return HttpResponse("Something went wrong.")
    # if account:
    #     context['id'] = account.id
    #     context['username'] = account.username
    #     context['email'] = account.email
    #     context['profile_image'] = account.profile_image.url
    #     context['hide_email'] = account.hide_email

    #     # Define template variables
    #     is_self = True
    #     user = request.user
    #     if user.is_authenticated and user != account:
    #     	is_self = False
    #     elif not user.is_authenticated:
    #     	is_self = False

    #     # Set the template variables to the values
    #     context['is_self'] = is_self
    #     context['BASE_URL'] = settings.BASE_URL
    # return render(request, "accounts/menu.html", context)

def dashboard_view(request):
    context = {}
    return render(request, 'accounts/dashboard.html', context)

@csrf_exempt
def test(request):
    context = {}
    return render(request, 'accounts/test.html', context)    

# global variable for diagnose_code
diagnose_code = 0

@csrf_exempt
def diagnose_view(request):
    # request should be ajax and method should be POST.
    # if request.method == 'POST' and request.is_ajax(): 
    # is_ajax is deprecated and removed since django 4.0
    if request.method == 'POST': 
        
        # delete old audio
        request.user.coughing_audio.delete()
        
        # recieve audio blob from ajax
        file = request.FILES.get('audio')
        print(f'ajax file recieved: {file}')
                
        # save audio to user model
        request.user.coughing_audio.save("coughing_audio.wav", file)
        request.user.save()
        
        # ready for KNN identifier
        # 1=healthy, 2=symtomatic
        audio_path = os.path.join(settings.BASE_DIR, f'media_cdn\coughing_audio\{request.user.pk}')
        diagnose_code = main("coughing_audio.wav", audio_path)
        # request.user.diagnose_code = 2
        request.user.diagnose_code = diagnose_code
        request.user.save()
        
        context = {}    
        return render(request, 'accounts/diagnose.html', context)
    
    context = {}    
    return render(request, 'accounts/diagnose.html', context)

def diagnose_result_view(request):
    context = {}
    return render(request, 'accounts/diagnose-result.html', context)

def profile_view(request):
    context = {}
    return render(request, 'accounts/profile.html', context)

def change_profile_view(request):
    context = {}
    return render(request, 'accounts/changeProfile.html', context)

def clinic_nearby_view(request):
    context = {}
    return render(request, 'accounts/clinicNearby.html', context)

def history_view(request):
    context = {}
    return render(request, 'accounts/history.html', context)

def logout_view(request):
    logout(request)
    return redirect("welcome")