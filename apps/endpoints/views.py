from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import views, status
from rest_framework.response import Response

from apps.ml.classifier.fasttext import FasttextClassifier
from apps.endpoints.forms import AuthorForm, LabelForm, LabelingByHandForm, LabelingForm
from apps.endpoints.models import Author, Label, LabelingByHand, LabelingToDo, LabelingOnGoing, LabelingDone

from django.db import transaction
from django.db.models import Count, Sum
from django.db.models import F
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

nb_labelingtodo_bylabel=2

#########################################
# LABELING BY HAND
#########################################

def labelingbyhand_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('labelingbyhand_label'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/labelingbyhand_author.html', {'form': form})

def labelingbyhand_label(request):
    author=request.session['author']
    if request.method == "POST":
        form = LabelForm(request.POST)
        if form.is_valid():
            request.session['label_in'] = form.cleaned_data['label_in']
            post = form.save(commit=False)
            post.author=author
            post.published_date = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse('labelingbyhand_prediction'))
    else:
        form = LabelForm()
    return render(request, 'endpoints/labelingbyhand_label.html', {'form': form})

def labelingbyhand_prediction(request):
    author=request.session['author']
    label_in=request.session['label_in']
    my_alg = FasttextClassifier()
    label_in_preprocessed=my_alg.preprocessing({"label_in": str(label_in)})
    prediction = my_alg.compute_prediction({"label_in": str(label_in)})["predictions"]
    df=pd.DataFrame(prediction)
    warning=True
    if (df['probability']>0.7).any():
        warning=False
    fichier_nomenclature=os.path.exists('nomenclature.csv')
    if fichier_nomenclature:
        nomenclature=pd.read_csv('nomenclature.csv', header=None)[0]
        nomenclature=[x.replace('__label__','').replace('_',' ') for x in nomenclature]
    else:
        nomenclature=list()

    if request.method == "POST":
        form = LabelingByHandForm()
        post = form.save(commit=False)    
        post.author=author
        post.label_in=label_in
        post.label_out=request.POST['label_out']
        if request.POST['label_out'] in list(df.prediction):
            post.probability=float(df[df.prediction==str(request.POST['label_out'])]["probability"])
        else:
            post.probability=float('nan')
        post.published_date = timezone.now() 
        post.save()
        return HttpResponseRedirect(reverse('labelingbyhand_label'))

    return render(request, 'endpoints/labelingbyhand_prediction.html', {'label_in':str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+')' ,
        'predictions':prediction, 'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})


#########################################
# LABELING FROM A FILE
#########################################

def labeling_author(request):
    request.session.flush()
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('labeling_groupChoice'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/labeling_author.html', {'form': form})

def labeling_groupChoice(request, nb_labelingtodo_bylabel=nb_labelingtodo_bylabel):
    author=request.session['author']
    idDone=list(LabelingDone.objects.filter(author=author).values_list('id_label', flat=True))
    groups=list(LabelingToDo.objects.exclude(id__in=idDone).annotate(nb=F('labeled')+F('ongoing')).filter(nb__lt=nb_labelingtodo_bylabel).values_list('categ', flat=True).distinct())
    if groups==list():
        return HttpResponseRedirect(reverse('labeling_final'))
    if request.method == "POST":
        if request.POST['groupselected'] in groups:
            request.session['groupselected']=request.POST['groupselected']
            return HttpResponseRedirect(reverse('labeling_prediction'))
        else:
            return HttpResponseRedirect(reverse('labeling_groupChoice'))
    return render(request, 'endpoints/labeling_groupChoice.html', {'groups': groups})

def labeling_prediction(request, nb_labelingtodo_bylabel=nb_labelingtodo_bylabel):
    author=request.session['author']
    groupselected=request.session['groupselected']
    
    idDone=LabelingDone.objects.filter(author=author).values_list('id_label', flat=True)
    idLabel=LabelingToDo.objects.filter(categ=groupselected).exclude(id__in=list(idDone)).annotate(nb=F('labeled')+F('ongoing')).filter(nb__lt=nb_labelingtodo_bylabel).values_list('id', flat=True).first()

    idOnGoing=LabelingOnGoing.objects.filter(author=author).filter(id_label__in=LabelingToDo.objects.filter(categ=groupselected).values_list('id', flat=True)).values_list('id_label', flat=True).first()
    if idOnGoing:
        idLabel=idOnGoing
        
    if idLabel==None:
        if 'idPostedLabel' in request.session :
            idPostedLabel=request.session['idPostedLabel']
            nb_ongoing=LabelingOnGoing.objects.filter(id_label=idPostedLabel).aggregate(Count('author', distinct=True))['author__count'] 
            nb_labeled=LabelingToDo.objects.filter(id=idPostedLabel).values('labeled').first()['labeled']

            if (nb_ongoing+nb_labeled)==nb_labelingtodo_bylabel:
                if idPostedLabel not in LabelingOnGoing.objects.filter(author=author).values_list('id_label', flat=True):
                    return HttpResponseRedirect(reverse('labeling_groupChoice'))
            if idPostedLabel in LabelingDone.objects.filter(author=author).values_list('id_label', flat=True):
                return HttpResponseRedirect(reverse('labeling_groupChoice'))

        if 'idPostedLabel' not in request.session :
            return HttpResponseRedirect(reverse('labeling_groupChoice'))
    else :      
        if idLabel not in LabelingOnGoing.objects.filter(author=author).values_list('id_label', flat=True):
            entry = LabelingOnGoing(id_label=idLabel,
                        author = author,
                        published_date = timezone.now()
                    )
            entry.save()

        entry = LabelingToDo.objects.get(id=idLabel)
        entry.ongoing = LabelingOnGoing.objects.filter(id_label=idLabel).aggregate(Count('author', distinct=True))['author__count'] 
        entry.save()
        
        label_in=str(LabelingToDo.objects.filter(id=idLabel).values('label_in').first()['label_in'])
        my_alg = FasttextClassifier()
        label_in_preprocessed=my_alg.preprocessing({"label_in": str(label_in)})
        prediction = my_alg.compute_prediction({"label_in": str(label_in)})["predictions"]
        df=pd.DataFrame(prediction)
        warning=True
        if (df['probability']>0.7).any():
            warning=False
        fichier_nomenclature=os.path.exists('nomenclature.csv')
        if fichier_nomenclature:
            nomenclature=pd.read_csv('nomenclature.csv', header=None)[0]
            nomenclature=[x.replace('__label__','').replace('_',' ') for x in nomenclature]
        else:
            nomenclature=list()

    if request.method == "POST":
        if 'idPostedLabel' not in request.session:
            idPostedLabel=idLabel
        else:
            idPostedLabel=request.session['idPostedLabel']
        postedLabel=LabelingToDo.objects.filter(id=idPostedLabel).values('label_in').first()['label_in']
        
        LabelingOnGoing.objects.filter(id_label=idPostedLabel).filter(author = author).delete()

        entry = LabelingToDo.objects.get(id=idPostedLabel)
        entry.ongoing = LabelingOnGoing.objects.filter(id_label=idPostedLabel).aggregate(Count('author', distinct=True))['author__count'] 
        entry.save()

        if 'label_out' in request.POST:
            my_alg = FasttextClassifier()
            prediction = my_alg.compute_prediction({"label_in": str(postedLabel)})["predictions"]
            posteddf=pd.DataFrame(prediction)

            entry = LabelingToDo.objects.get(id=idPostedLabel)
            entry.labeled +=1
            entry.save()

            if request.POST['label_out'] in list(posteddf.prediction):
                entry=LabelingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        label_out = request.POST['label_out'],
                        probability = float(posteddf[posteddf.prediction==str(request.POST['label_out'])]["probability"]),
                        published_date = timezone.now()
                    )
                entry.save()
            else:
                entry=LabelingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        label_out = request.POST['label_out'],
                        probability = float('nan'),
                        published_date = timezone.now()
                    )
                entry.save()
                
            return HttpResponseRedirect(reverse('labeling_prediction'))
        if 'stop' in request.POST:
            request.session.flush()
            return HttpResponseRedirect(reverse('labeling_summary'))
        if 'unknown' in request.POST:
            entry=LabelingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        published_date = timezone.now(),
                        unknown=True
                    )
            entry.save()

            if idLabel==None:
                return HttpResponseRedirect(reverse('labeling_groupChoice'))
            else:
                return HttpResponseRedirect(reverse('labeling_prediction'))

    if idLabel:
        request.session['idPostedLabel']=idLabel
        ean=LabelingToDo.objects.filter(id=idLabel).values('ean').first()
        if ean['ean']==None:
            affichage=str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+')'
        else:
            affichage=str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+') avec pour EAN '+str(ean['ean'])
    
    return render(request, 'endpoints/labeling_prediction.html', {'label_in': affichage, 'predictions':prediction, 
            'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})

def labeling_summary(request):
    nb_labeled_atLeastOnce=LabelingToDo.objects.filter(labeled__gt=0).count()
    nb_labeled=LabelingToDo.objects.filter(labeled=nb_labelingtodo_bylabel).count()
    nb_total=LabelingToDo.objects.count()

    total=list(LabelingToDo.objects.all().values('categ').annotate(total=Count('categ')))            
    labeledAtLeastOnce=list(LabelingToDo.objects.all().filter(labeled__gt=0).values('categ').annotate(labeledatleastOnce=Count('categ'))) 
    labeled=list(LabelingToDo.objects.all().filter(labeled=nb_labelingtodo_bylabel).values('categ').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbygroup=pd.DataFrame(total)
    resbygroup=resbygroup.groupby('categ').max().fillna(0).astype(int).reset_index().to_dict('records')  

    if request.method == "POST":
        return HttpResponseRedirect(reverse('labeling_author'))
    return render(request, 'endpoints/labeling_summary.html', {'nb_labeled':nb_labeled_atLeastOnce, 'nb_total':nb_total,
        'resbygroup':resbygroup})

def labeling_final(request):
    author=request.session['author']
    nb_labeled_atLeastOnce=LabelingToDo.objects.filter(labeled__gt=0).count()
    nb_total=LabelingToDo.objects.count()

    total=list(LabelingToDo.objects.values('categ').annotate(total=Count('categ')))           
    labeledAtLeastOnce=list(LabelingToDo.objects.all().filter(labeled__gt=0).values('categ').annotate(labeledatleastOnce=Count('categ')))
    labeled=list(LabelingToDo.objects.all().filter(labeled=nb_labelingtodo_bylabel).values('categ').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbygroup=pd.DataFrame(total)
    resbygroup=resbygroup.groupby('categ').max().fillna(0).astype(int).reset_index().to_dict('records')

    if request.method == "POST":
        if 'unknown' in request.POST:
            reinit=LabelingDone.objects.filter(author=author).filter(unknown=True).all()
            reinit.delete()
            return HttpResponseRedirect(reverse('labeling_groupChoice'))
        if 'labelingbyhand' in request.POST:
            return HttpResponseRedirect(reverse('labelingbyhand_label'))
    return render(request, 'endpoints/labeling_final.html', {'nb_labeled':nb_labeled_atLeastOnce, 'nb_total':nb_total, 'resbygroup':resbygroup})
