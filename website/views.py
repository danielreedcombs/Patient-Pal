from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.template import RequestContext
from website.forms import UserForm
from website.models import medication
from django.db import connection
from django.urls import reverse
from website.forms import add_medication

import datetime

def index(request):
    template_name = 'index.html'
    return render(request, template_name, {})


# Create your views here.
def register(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        return login_user(request)

    elif request.method == 'GET':
        user_form = UserForm()
        template_name = 'register.html'
        return render(request, template_name, {'user_form': user_form})


def login_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # Obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, log the user in
        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('home')

        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")


    return render(request, 'login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage. Is there a way to not hard code
    # in the URL in redirects?????
    return HttpResponseRedirect('/')


@login_required
def homepage(request):
    context ={}
    return render(request, 'product/homepage.html', context)

@login_required
def doctors_notes(request):
    context ={}
    return render(request, 'product/notes.html', context)

@login_required
def doctors_appointments(request):
    context ={}
    return render(request, 'product/appointments.html', context)

@login_required
def medications(request):
    user_id = request.user.id
    medications = medication.objects.all().filter(deletedOn = None)

    context = { 'medications': medications , 'user': user_id}
    return render(request, 'product/medications.html', context)

@login_required
def deletemedication(request, id):
    date = datetime.date.today()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE website_medication
                                SET deletedOn = %s
                                where website_medication.id = %s''', [date, id])
            return HttpResponseRedirect(reverse('website:medications'))



    except medication.DoesNotExist:
        raise Http404("medication does not exist")

@login_required
def addmedication(request):
    context ={'name':'hello'}
    return render(request, 'product/addmedication.html', context)

@login_required
def addmedications(request):

    if request.method == 'GET':
        medication_form = add_medication()
        template_name = 'product/addmedication.html'
        return render(request, template_name, {'medication_form': medication_form})


    if request.method == "POST":
        patient_id = request.user.id
        name = request.POST["name"]
        dosage = request.POST["dosage"]
        id = None
        deletedOn = None

    with connection.cursor() as cursor:
        cursor.execute("INSERT into website_medication VALUES(%s, %s, %s, %s, %s)", [id, name, dosage, deletedOn, patient_id])
        return HttpResponseRedirect(reverse('website:medications'))

@login_required
def edit_medication(request ,id):
    medications = get_object_or_404(medication, pk=id)
    if request.method == "POST":
        name_post = request.POST["name"]
        dosage_post= request.POST["dosage"]
        medications.name = name_post
        medications.dosage = dosage_post
        medications.save()
        return HttpResponseRedirect(reverse('website:medications'))


    context = {'medication' : medications}
    template_name = 'product/editmedication.html'
    return render(request, template_name , context)