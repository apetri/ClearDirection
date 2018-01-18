from django.urls import path,re_path

from . import views

app_name = "lookup"

urlpatterns = [

	re_path('message/(?P<section>.+)/(?P<result>.+)',views.logSubmission, name='logsubmission'),
    
    #path('table/', views.sampleTable, name='table'),
    #re_path('form/[\?]?',views.sampleForm, name='form'),
    
    re_path('query/[\?]?',views.queryPerson, name='query'),
    re_path('insert/[\?]?',views.insertPerson, name='insert'),
    re_path('log/[\?]?',views.logSecret, name='log'),

    #re_path('query/[\?]?',views.queryPersonDoNothing, name='query'),
    #re_path('insert/[\?]?',views.insertPersonDoNothing, name='insert'),
    #re_path('log/[\?]?',views.logSecretDoNothing, name='log'),

]