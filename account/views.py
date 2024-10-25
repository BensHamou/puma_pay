from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib import messages 
from .decorators import *
from .filters import *
from .models import *
from .forms import *
import requests
import json


# USERS

@login_required(login_url='login')
@admin_only_required
def homeView(request):
    context = { 'content': 'content' }
    return render(request, 'home.html', context)

@login_required(login_url='login')
@admin_only_required
def refreshUserList(request):
    usernames = User.objects.values_list('username', flat=True)
    API_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'
    GROUP_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users/group/PUMA-LABS?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'
    response = requests.get(API_Users)
    response_ = requests.get(GROUP_Users)
    if response.status_code == 200 and response_.status_code == 200:
        data = json.loads(response.content)
        group_users = json.loads(response_.content)['members']
        new_users_list = [user for user in data['users'] if user['fullname'] in group_users and user['AD2000'] not in usernames]
        for user in new_users_list:
            user = User(username= user['AD2000'], password='password', fullname=user['fullname'], role='Nouveau', is_admin=False, first_name= user['fname'], email= user['mail'], last_name = user['lname'])
            user.save()
    else:
        print('Error: could not fetch data from API')
    cache_param = str(uuid.uuid4())
    url_path = reverse('users')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_only_required
def editUserView(request, id):
    user = User.objects.get(id=id)
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save(user=request.user)
            form.save_m2m()
            url_path = reverse('users')
            return redirect(getRedirectionURL(request, url_path))
    context = {'form': form, 'user_': user }
    return render(request, 'user_form.html', context)

@login_required(login_url='login')
@admin_only_required
def deleteUserView(request, id):
    user = get_object_or_404(User, id=id)
    try:
        user.delete()
        url_path = reverse('users')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression d'utilisateur: {e}")
        return redirect(getRedirectionURL(request, reverse('users')))

@login_required(login_url='login')
@admin_only_required
def listUserView(request):
    users = User.objects.exclude(username='admin').order_by('-date_modified')
    filteredData = UserFilter(request.GET, queryset=users)
    users = filteredData.qs
    paginator = Paginator(users, request.GET.get('page_size', 12))
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filteredData': filteredData}
    return render(request, 'list_users.html', context)

# AUTHENTIFICATION

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

def logoutView(request):
    logout(request)
    return redirect('login')

# ZONES

@login_required(login_url='login')
@admin_required
def listZoneView(request):
    zones = Zone.objects.all().order_by('-date_modified')
    filteredData = ZoneFilter(request.GET, queryset=zones)
    zones = filteredData.qs
    paginator = Paginator(zones, request.GET.get('page_size', 12))
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filteredData': filteredData}
    return render(request, 'list_zones.html', context)

@login_required(login_url='login')
@admin_required
def deleteZoneView(request, id):
    zone = get_object_or_404(Zone, id=id)
    try:
        zone.delete()
        url_path = reverse('zones')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de la zone: {e}")
        return redirect(getRedirectionURL(request, reverse('zones')))

@login_required(login_url='login')
@admin_required
def createZoneView(request):
    form = ZoneForm()
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('zones')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form}
    return render(request, 'zone_form.html', context)

@login_required(login_url='login')
@admin_required
def editZoneView(request, id):
    zone = get_object_or_404(Zone, id=id)
    form = ZoneForm(instance=zone)
    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('zones')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form, 'zone': zone}
    return render(request, 'zone_form.html', context)

# OBJECTIVES

@login_required(login_url='login')
@admin_required
def listObjectiveView(request):
    objectives = Objective.objects.all().order_by('-date_modified')
    filteredData = ObjectiveFilter(request.GET, queryset=objectives)
    objectives = filteredData.qs
    paginator = Paginator(objectives, request.GET.get('page_size', 12))
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filteredData': filteredData}
    return render(request, 'list_objectives.html', context)

@login_required(login_url='login')
@admin_required
def deleteObjectiveView(request, id):
    objective = get_object_or_404(Objective, id=id)
    try:
        objective.delete()
        url_path = reverse('objectives')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de l'objectif: {e}")
        return redirect(getRedirectionURL(request, reverse('objectives')))

@login_required(login_url='login')
@admin_required
def createObjectiveView(request):
    form = ObjectiveForm()
    if request.method == 'POST':
        form = ObjectiveForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('objectives')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form}
    return render(request, 'objective_form.html', context)

@login_required(login_url='login')
@admin_required
def editObjectiveView(request, id):
    objective = get_object_or_404(Objective, id=id)
    form = ObjectiveForm(instance=objective)
    if request.method == 'POST':
        form = ObjectiveForm(request.POST, instance=objective)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('objectives')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form, 'objective': objective}
    return render(request, 'objective_form.html', context)

