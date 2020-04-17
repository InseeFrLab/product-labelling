from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import views, status
from rest_framework.response import Response

from apps.ml.classifier.fasttext import FasttextClassifier
from apps.endpoints.forms import AuthorForm, PostForm, PredictionForm
from apps.endpoints.models import Author, Post, Labellisation

from django.db import transaction
from django.shortcuts import render

from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

import os
import json
from numpy.random import rand
import pandas as pd

def post_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse('post_new'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/post_author.html', {'form': form})

def post_new(request):
    author=request.session['author']
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            request.session['libelle'] = form.cleaned_data['libelle']
            post = form.save(commit=False)
            post.author=author
            post.published_date = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse('post_list'))
    else:
        form = PostForm()
    return render(request, 'endpoints/post_edit.html', {'form': form})

def post_list(request):
    author=request.session['author']
    libelle=request.session['libelle']
    my_alg = FasttextClassifier()
    prediction = my_alg.compute_prediction({"libelle": str(libelle)})["predictions"]
    df=pd.DataFrame(prediction)
    warning=True
    if (df['prediction']>0.7).any():
        warning=False
    fichier_nomenclature=os.path.exists('nomenclature.csv')
    if fichier_nomenclature:
        nomenclature=pd.read_csv('nomenclature.csv', header=None)[0]
    else:
        nomenclature=list()

    if request.method == "POST":
        form = PredictionForm()
        post = form.save(commit=False)    
        post.author=author           
        post.libelle=libelle
        post.label=request.POST['label']
        if request.POST['label'] in df.label:
            post.prediction=float(df[df.label==str(request.POST['label'])]["prediction"])
        else:
            post.prediction=float('nan')
        post.published_date = timezone.now() 
        post.save()
        return HttpResponseRedirect(reverse('post_new'))

    return render(request, 'endpoints/post_list.html', {'libelle':str(libelle).upper,'predictions':prediction, 'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})

