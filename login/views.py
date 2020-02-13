from django.shortcuts import render
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
import json
import requests
from bs4 import BeautifulSoup
from .forms import UserForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.db import transaction

from allauth.account.forms import LoginForm

"""class MyCustomLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        # Add your own processing here.
        # You must return the original result.
        save_user(self, request, user, form)
        return super(MyCustomLoginForm, self).login(*args, **kwargs)"""

def home(request):
    return render(request, 'login/home.html')

def index(request):
    extra_data = []
    if request.user.is_authenticated:
        extra_data = request.user.socialaccount_set.all()[0].extra_data
    return render(request, 'login/index.html', {'extra_data': extra_data})

def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('login:home', args=()))

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            print('Your profile was successfully updated!')
            return redirect('login:home')
        else:
            print('Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'login/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def schools(request):
    classes = get_classes()
    school_data = get_schools()
    school_list = list(school_data.keys())
    section_list = list(school_data.values())
    return render(request, 'login/schools.html', {'school_list': school_list, 'section_list': section_list, 'classes': classes})

def courses(request):
    courses = request.session['courses']
    return render(request, 'login/courses.html', {'courses':courses})

def get_section(request):
    try:
        courses = []
        link = request.POST['choice']
        courses = get_courses(link)
        request.session['courses'] = json.dumps(courses)
    except:
        school_data = get_schools()
        school_list = list(school_data.keys())
        section_list = list(school_data.values())
        return render(request, 'login/schools.html', {'school_list': school_list, 'section_list': section_list})
    return HttpResponseRedirect(reverse('login:courses'))

def get_courses(url):
    link = url
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        classes = []
        try:
            names = soup.find_all( class_="CourseName")
            for name in names:
                parts = name.get('onclick').split(',')
                dept = parts[0].split("'")[1]
                number = parts[1].split("'")[1]
                course_name = name.get_text()
                classes.append((dept, number, course_name))
        except:
            None
        return classes
    else:
        return []

def get_schools():
    with open('staticfiles/login/class_sections.txt') as json_file:
        schools = json.load(json_file)
        return schools

def get_classes():
    with open('staticfiles/login/classes.txt') as json_file:
        data = json.load(json_file)
        return json.dumps(data)
