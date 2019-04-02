from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.template import RequestContext
from website.forms import UserForm
from website.models import medication, doctors_visits, Notes, doctors_notes
from django.db import connection
from django.urls import reverse
from website.forms import add_medication
import datetime

def index(request):
    template_name = 'index.html'
    return render(request, template_name, {})


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True

        return login_user(request)

    elif request.method == 'GET':
        user_form = UserForm()
        template_name = 'register.html'
        return render(request, template_name, {'user_form': user_form})


def login_user(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('home')

        else:
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    return render(request, 'login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def homepage(request):
    context ={}
    #this renders the generic homepage
    return render(request, 'product/homepage.html', context)


@login_required
def doctors_appointments(request):
    #grabbing the spacific user
    user_id = request.user.id
    # searching throughout all the appointments for the ones that have not been deleted.
    appointments = doctors_visits.objects.all().filter(deletedOn = None)
    # gets all notes that have not been deleted.
    notes = doctors_notes.objects.all().filter(deletedOn=None)
    context ={'appointments' : appointments , 'user' : user_id , 'notes' : notes}
    return render(request, 'product/appointments.html', context)


@login_required
def medications(request):
    # getting the users information
    user_id = request.user.id
    # getting all medications that have not been deleted
    medications = medication.objects.all().filter(deletedOn = None)

    context = { 'medications': medications , 'user': user_id}
    return render(request, 'product/medications.html', context)


@login_required
def deletemedication(request, id):
    # getting the date
    date = datetime.date.today()
    # writing a raw SQL query that adds the date to the deletedOn column of the medication.
    try:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE website_medication
                                SET deletedOn = %s
                                where website_medication.id = %s''', [date, id])
            return HttpResponseRedirect(reverse('website:medications'))

    except medication.DoesNotExist:
        raise Http404("medication does not exist")


@login_required
def addmedications(request):
    # if the method is a get then go obtain all the medications and and put them into the template and render it
    if request.method == 'GET':
        medication_form = add_medication()
        template_name = 'product/addmedication.html'
        return render(request, template_name, {'medication_form': medication_form})

    # if posting grab these values out of the form, and write this raw SQL statement and insert the values.
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
    # get the individual medication with the Id that was passed down.
    medications = get_object_or_404(medication, pk=id)
    # post these values over the medication that has the id we have obtained.
    if request.method == "POST":
        name_post = request.POST["name"]
        dosage_post= request.POST["dosage"]
        medications.name = name_post
        medications.dosage = dosage_post
        medications.save()
        # send them back to the list of the users medications.
        return HttpResponseRedirect(reverse('website:medications'))

    context = {'medication' : medications}
    template_name = 'product/editmedication.html'
    return render(request, template_name , context)


@login_required
def edit_appointment(request, id):
    # get the individual appointment that has the Id that was passed down to the method.
    appointments = get_object_or_404(doctors_visits, pk=id)
    # post over this appointment with these new values
    if request.method == "POST":
        name = request.POST["name"]
        location = request.POST["location"]
        date = request.POST["date"]
        time = request.POST["time"]
        appointments.doctors_name = name
        appointments.location = location
        appointments.date = date
        appointments.time = time
        appointments.save()
        # redirect to the list of all appointments for the user
        return HttpResponseRedirect(reverse('website:appointments'))

    context = {'appointment' : appointments}
    template_name = 'product/editappointments.html'
    return render(request, template_name , context)


@login_required
def add_appointment(request):
    # obtain the user that is currently logged in
    user_id = request.user
    # post a new appointment for the user with these values from the form.
    if request.method == "POST":
        new_appointment = doctors_visits(
        doctors_name = request.POST["name"],
        location = request.POST["location"],
        date = request.POST["date"],
        time = request.POST["time"],
        patient = user_id,)
        new_appointment.save()
        # send them back to all there appointments.
        return HttpResponseRedirect(reverse('website:appointments'))

    template_name = 'product/addappointment.html'
    return render(request, template_name)


@login_required
def delete_appointment(request, id):
    # obtain todays date
    date = datetime.date.today()
    # a raw SQL query that plugs the date into the deletedOn column for the doctors visit.
    try:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE website_doctors_visits
                                SET deletedOn = %s
                                where id = %s''', [date, id])
        return HttpResponseRedirect(reverse('website:appointments'))

    except appointments.DoesNotExist:
        raise Http404("appointment does not exist")

    
@login_required
def add_note(request):
    user_id = request.user
    if request.method == 'GET':
        appointments = doctors_visits.objects.filter(patient_id = user_id.id)
        template_name = 'product/notes.html'
        context = {'appointments': appointments , "user_id" : user_id}
        return render(request, template_name, context)

    if request.method == "POST":
        new_notes = Notes( user = user_id , note = request.POST["note"],)
        new_notes.save()
        newdoc = doctors_visits.objects.get(pk= request.POST["appointment"])
        new_joint_table = doctors_notes(doctors_vist = newdoc , notes = new_notes,)
        new_joint_table.save()
        return HttpResponseRedirect(reverse('website:note'))


@login_required
def appointment_notes(request, id):
    notes = doctors_notes.objects.all().filter(deletedOn=None)
    appointment = id
    context= {'notes' : notes , 'appointment' : appointment}
    template_name = 'product/appointmentNote.html'
    return render(request, template_name , context)


@login_required
def note_delete(request, id):
    date = datetime.date.today()
    user_id = request.user.id
    joint_table= get_object_or_404(doctors_notes, id = id)
    joint_table.deletedOn = date
    joint_table.save()
    note = get_object_or_404(Notes, id= joint_table.notes_id )
    note.deletedOn = date
    note.save()
    return HttpResponseRedirect(reverse('website:appointments'))