from django.conf.urls import url
from django.urls import path

from . import views

app_name = "website"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    path('home', views.homepage, name='home'),
    path('notes', views.doctors_notes, name='notes'),
    path('appointments', views.doctors_appointments, name='appointments'),
    path('medications', views.medications, name='medications'),
    path('addmedication', views.addmedications, name='addmedications'),
    path('deletemedication/<int:id>', views.deletemedication, name='deletemedication'),

]