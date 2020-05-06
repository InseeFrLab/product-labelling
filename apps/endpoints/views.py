from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import views, status
from rest_framework.response import Response

from apps.ml.classifier.fasttext import FasttextClassifier
from apps.endpoints.forms import AuthorForm, PostForm, PredictionForm
from apps.endpoints.models import Author, Post, LabellisationManuelle, Labellisation

from django.db import transaction
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import os
import json
import csv
from numpy.random import rand
import pandas as pd

def post_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('post_libelle'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/post_author.html', {'form': form})

def post_libelle(request):
    author=request.session['author']
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            request.session['libelle'] = form.cleaned_data['libelle']
            post = form.save(commit=False)
            post.author=author
            post.published_date = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse('post_listprediction'))
    else:
        form = PostForm()
    return render(request, 'endpoints/post_libelle.html', {'form': form})

def post_listprediction(request):
    author=request.session['author']
    libelle=request.session['libelle']
    my_alg = FasttextClassifier()
    libelle_preprocessed=my_alg.preprocessing({"libelle": str(libelle)})
    prediction = my_alg.compute_prediction({"libelle": str(libelle)})["predictions"]
    df=pd.DataFrame(prediction)
    warning=True
    if (df['prediction']>0.7).any():
        warning=False
    fichier_nomenclature=os.path.exists('nomenclature.csv')
    if fichier_nomenclature:
        nomenclature=pd.read_csv('nomenclature.csv', header=None)[0]
        nomenclature=[x.replace('__label__','').replace('_',' ') for x in nomenclature]
    else:
        nomenclature=list()

    if request.method == "POST":
        form = PredictionForm()
        post = form.save(commit=False)    
        post.author=author           
        post.libelle=libelle
        post.label=request.POST['label']
        if request.POST['label'] in list(df.label):
            post.prediction=float(df[df.label==str(request.POST['label'])]["prediction"])
        else:
            post.prediction=float('nan')
        post.published_date = timezone.now() 
        post.save()
        return HttpResponseRedirect(reverse('post_libelle'))

    return render(request, 'endpoints/post_listprediction.html', {'libelle':str(libelle)+' (transformé par preprocessing en : '+str(libelle_preprocessed)+')' ,'predictions':prediction, 'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})

def post_author_labellisation(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('post_labellisation'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/post_author_labellisation.html', {'form': form})

def post_labellisation(request):
    author=request.session['author']
    libelle=Labellisation.objects.values('libelle').exclude(encours=True).first()
    if libelle==None:
        return HttpResponseRedirect(reverse('post_final'))
    else :
        libelle=str(libelle['libelle'])
        entry = Labellisation.objects.get(libelle=libelle)
        entry.encours = True
        entry.save()
        
        my_alg = FasttextClassifier()
        libelle_preprocessed=my_alg.preprocessing({"libelle": str(libelle)})
        prediction = my_alg.compute_prediction({"libelle": str(libelle)})["predictions"]
        df=pd.DataFrame(prediction)
        warning=True
        if (df['prediction']>0.7).any():
            warning=False
        fichier_nomenclature=os.path.exists('nomenclature.csv')
        if fichier_nomenclature:
            nomenclature=pd.read_csv('nomenclature.csv', header=None)[0]
            nomenclature=[x.replace('__label__','').replace('_',' ') for x in nomenclature]
        else:
            nomenclature=list()

        if request.method == "POST":
            entry = Labellisation.objects.get(libelle=libelle)
            entry.encours = None
            entry.save()
            if 'label' in request.POST:
                postedlibelle=request.session['postedlibelle']
                posteddf=request.session['posteddf']
                my_alg = FasttextClassifier()
                prediction = my_alg.compute_prediction({"libelle": str(postedlibelle)})["predictions"]
                posteddf=pd.DataFrame(prediction)               
                entry = Labellisation.objects.get(libelle=postedlibelle)
                entry.labellise=True 
                entry.author=author
                entry.label=request.POST['label']
                if request.POST['label'] in list(posteddf.label):
                    entry.prediction=float(posteddf[posteddf.label==str(request.POST['label'])]["prediction"])
                else:
                    entry.prediction=float('nan')
                entry.published_date = timezone.now() 
                entry.save()
                return HttpResponseRedirect(reverse('post_labellisation'))
            if 'encours' in request.POST:
                postedlibelle=request.session['postedlibelle']
                entry = Labellisation.objects.get(libelle=postedlibelle)
                entry.encours = None
                entry.save()
                return HttpResponseRedirect(reverse('post_bilanlabellisation'))

    request.session['postedlibelle']=libelle
    return render(request, 'endpoints/post_labellisation.html', {'libelle':str(libelle)+' (transformé par preprocessing en : '+str(libelle_preprocessed)+')' ,
        'predictions':prediction, 'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})

def post_bilanlabellisation(request):
    nb_labellise=Labellisation.objects.filter(labellise=True).count()
    nb_total=Labellisation.objects.count()
    if request.method == "POST":
        return HttpResponseRedirect(reverse('post_author_labellisation'))
    return render(request, 'endpoints/post_bilanlabellisation.html', {'nb_labellise':nb_labellise, 'nb_total':nb_total})

def post_final(request):
    nb_labellise=Labellisation.objects.filter(labellise=True).count() 
    if request.method == "POST":
        return HttpResponseRedirect(reverse('post_libelle'))
    return render(request, 'endpoints/post_final.html', {'nb_labellise':nb_labellise})

def post_loadfile(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        nb_lines=0
        first_lines=[]
        with open(os.path.join(settings.MEDIA_ROOT,filename), 'r', encoding=request.POST['encoding']) as file:
            reader = csv.reader(file, delimiter=request.POST['separator'])
            for row in reader:
                libelle = Labellisation(libelle=row[0])
                libelle.save()
                nb_lines+=1
                if nb_lines<4:
                    first_lines.append(row[0])

        return render(request, 'endpoints/post_loadfile.html', {'uploaded_file_url': uploaded_file_url, 'first_lines':first_lines, 'nb_lines':nb_lines})
    return render(request, 'endpoints/post_loadfile.html')
