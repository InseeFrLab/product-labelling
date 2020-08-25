from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import views, status
from rest_framework.response import Response

from apps.ml.classifier.fasttext import FasttextClassifier
from apps.endpoints.forms import AuthorForm, LabelForm, labellingByHandForm, labellingForm
from apps.endpoints.models import Author, Label, labellingByHand, labellingToDo, labellingOnGoing, labellingDone

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

nb_labellingtodo_bylabel=2

#########################################
# labelling BY HAND
#########################################

def labellingbyhand_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('labellingbyhand_label'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/labellingbyhand_author.html', {'form': form})

def labellingbyhand_label(request):
    author=request.session['author']
    if request.method == "POST":
        form = LabelForm(request.POST)
        if form.is_valid():
            request.session['label_in'] = form.cleaned_data['label_in']
            post = form.save(commit=False)
            post.author=author
            post.published_date = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse('labellingbyhand_prediction'))
    else:
        form = LabelForm()
    return render(request, 'endpoints/labellingbyhand_label.html', {'form': form})

def labellingbyhand_prediction(request):
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
        form = labellingByHandForm()
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
        return HttpResponseRedirect(reverse('labellingbyhand_label'))

    return render(request, 'endpoints/labellingbyhand_prediction.html', {'label_in':str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+')' ,
        'predictions':prediction, 'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})


#########################################
# labelling FROM A FILE
#########################################

def labelling_author(request):
    request.session.flush()
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            request.session['author'] = form.cleaned_data['name']
            post = form.save(commit=False)
            return HttpResponseRedirect(reverse('labelling_tableChoice'))
    else:
        form = AuthorForm()
    return render(request, 'endpoints/labelling_author.html', {'form': form})

def labelling_tableChoice(request, nb_labellingtodo_bylabel=nb_labellingtodo_bylabel):
    author=request.session['author']
    idDone=list(labellingDone.objects.filter(author=author).values_list('id_label', flat=True))
    tables=labellingToDo.objects.exclude(id__in=idDone).annotate(nb=F('labeled')+F('ongoing')).filter(nb__lt=nb_labellingtodo_bylabel).values_list('table_name', flat=True).distinct()
    if tables==list():
        return HttpResponseRedirect(reverse('labelling_final'))
    if request.method == "POST":
        if request.POST['tableselected'] in tables:
            request.session['tableselected']=request.POST['tableselected']
            return HttpResponseRedirect(reverse('labelling_groupChoice'))
        else:
            return HttpResponseRedirect(reverse('labelling_tableChoice'))
    return render(request, 'endpoints/labelling_tableChoice.html', {'tables': tables})

def labelling_groupChoice(request, nb_labellingtodo_bylabel=nb_labellingtodo_bylabel):
    author=request.session['author']
    tableselected=request.session['tableselected']
    idDone=list(labellingDone.objects.filter(author=author).values_list('id_label', flat=True))
    groups=list(labellingToDo.objects.filter(table_name=tableselected).exclude(id__in=idDone).annotate(nb=F('labeled')+F('ongoing')).filter(nb__lt=nb_labellingtodo_bylabel).values_list('categ', flat=True).distinct())
    if groups==list():
        return HttpResponseRedirect(reverse('labelling_final'))
    if request.method == "POST":
        if request.POST['groupselected'] in groups:
            request.session['groupselected']=request.POST['groupselected']
            return HttpResponseRedirect(reverse('labelling_prediction'))
        else:
            return HttpResponseRedirect(reverse('labelling_groupChoice'))
    return render(request, 'endpoints/labelling_groupChoice.html', {'groups': groups})

def labelling_prediction(request, nb_labellingtodo_bylabel=nb_labellingtodo_bylabel):
    author=request.session['author']
    tableselected=request.session['tableselected']
    groupselected=request.session['groupselected']
    
    idDone=labellingDone.objects.filter(author=author).values_list('id_label', flat=True)
    idLabel=labellingToDo.objects.filter(table_name=tableselected).filter(categ=groupselected).exclude(id__in=list(idDone)).annotate(nb=F('labeled')+F('ongoing')).filter(nb__lt=nb_labellingtodo_bylabel).values_list('id', flat=True).first()

    idOnGoing=labellingOnGoing.objects.filter(author=author).filter(id_label__in=labellingToDo.objects.filter(table_name=tableselected).filter(categ=groupselected).values_list('id', flat=True)).values_list('id_label', flat=True).first()
    if idOnGoing:
        idLabel=idOnGoing
        
    if idLabel==None:
        if 'idPostedLabel' in request.session :
            idPostedLabel=request.session['idPostedLabel']
            nb_ongoing=labellingOnGoing.objects.filter(id_label=idPostedLabel).aggregate(Count('author', distinct=True))['author__count'] 
            nb_labeled=labellingToDo.objects.filter(id=idPostedLabel).values('labeled').first()['labeled']

            if (nb_ongoing+nb_labeled)==nb_labellingtodo_bylabel:
                if idPostedLabel not in labellingOnGoing.objects.filter(author=author).values_list('id_label', flat=True):
                    return HttpResponseRedirect(reverse('labelling_groupChoice'))
            if idPostedLabel in labellingDone.objects.filter(author=author).values_list('id_label', flat=True):
                return HttpResponseRedirect(reverse('labelling_groupChoice'))

        if 'idPostedLabel' not in request.session :
            return HttpResponseRedirect(reverse('labelling_groupChoice'))
    else :      
        if idLabel not in labellingOnGoing.objects.filter(author=author).values_list('id_label', flat=True):
            entry = labellingOnGoing(id_label=idLabel,
                        author = author,
                        published_date = timezone.now()
                    )
            entry.save()

        entry = labellingToDo.objects.get(id=idLabel)
        entry.ongoing = labellingOnGoing.objects.filter(id_label=idLabel).aggregate(Count('author', distinct=True))['author__count'] 
        entry.save()
        
        label_in=str(labellingToDo.objects.filter(id=idLabel).values('label_in').first()['label_in'])
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
        postedLabel=labellingToDo.objects.filter(id=idPostedLabel).values('label_in').first()['label_in']
        
        labellingOnGoing.objects.filter(id_label=idPostedLabel).filter(author = author).delete()

        entry = labellingToDo.objects.get(id=idPostedLabel)
        entry.ongoing = labellingOnGoing.objects.filter(id_label=idPostedLabel).aggregate(Count('author', distinct=True))['author__count'] 
        entry.save()

        if 'label_out' in request.POST:
            my_alg = FasttextClassifier()
            prediction = my_alg.compute_prediction({"label_in": str(postedLabel)})["predictions"]
            posteddf=pd.DataFrame(prediction)

            entry = labellingToDo.objects.get(id=idPostedLabel)
            entry.labeled +=1
            entry.save()

            if request.POST['label_out'] in list(posteddf.prediction):
                entry=labellingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        label_out = request.POST['label_out'],
			categ=labellingToDo.objects.filter(id=postedLabel).values_list('categ', flat=True).first(),
                        probability = float(posteddf[posteddf.prediction==str(request.POST['label_out'])]["probability"]),
                        published_date = timezone.now()
                    )
                entry.save()
            else:
                entry=labellingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        label_out = request.POST['label_out'],
			categ=labellingToDo.objects.filter(id=postedLabel).values_list('categ', flat=True).first(),
                        probability = float('nan'),
                        published_date = timezone.now()
                    )
                entry.save()
                
            return HttpResponseRedirect(reverse('labelling_prediction'))
        if 'stop' in request.POST:
            request.session.flush()
            return HttpResponseRedirect(reverse('labelling_summary'))
        if 'unknown' in request.POST:
            entry=labellingDone(id_label=idPostedLabel,
                        label_in = postedLabel,
                        author = author,
                        published_date = timezone.now(),
                        unknown=True
                    )
            entry.save()

            if idLabel==None:
                return HttpResponseRedirect(reverse('labelling_groupChoice'))
            else:
                return HttpResponseRedirect(reverse('labelling_prediction'))

    if idLabel:
        request.session['idPostedLabel']=idLabel
        ean=labellingToDo.objects.filter(id=idLabel).values('ean').first()
        if ean['ean']==None:
            affichage=str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+')'
        else:
            affichage=str(label_in)+' (transformé par preprocessing en : '+str(label_in_preprocessed)+') avec pour EAN '+str(ean['ean'])
    
    return render(request, 'endpoints/labelling_prediction.html', {'label_in': affichage, 'predictions':prediction, 
            'nomenclature':nomenclature, 'fichier_nomenclature':fichier_nomenclature, 'warning':warning})

def labelling_summary(request):
    total=list(labellingToDo.objects.values('table_name').annotate(total=Count('table_name')))           
    labeledAtLeastOnce=list(labellingToDo.objects.all().filter(labeled__gt=0).values('table_name').annotate(labeledatleastOnce=Count('categ')))
    labeled=list(labellingToDo.objects.all().filter(labeled=nb_labellingtodo_bylabel).values('table_name').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbytable=pd.DataFrame(total)
    resbytable=resbytable.groupby('table_name').max().fillna(0).astype(int).reset_index().to_dict('records')

    total=list(labellingToDo.objects.all().values('table_name','categ').annotate(total=Count('categ')))            
    labeledAtLeastOnce=list(labellingToDo.objects.all().filter(labeled__gt=0).values('table_name','categ').annotate(labeledatleastOnce=Count('categ'))) 
    labeled=list(labellingToDo.objects.all().filter(labeled=nb_labellingtodo_bylabel).values('table_name','categ').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbygroup=pd.DataFrame(total)
    resbygroup=resbygroup.groupby(['table_name', 'categ']).max().fillna(0).astype(int).reset_index().to_dict('records')  

    if request.method == "POST":
        return HttpResponseRedirect(reverse('labelling_author'))
    return render(request, 'endpoints/labelling_summary.html', {'resbytable':resbytable,
        'resbygroup':resbygroup})

def labelling_final(request):
    author=request.session['author']
    
    total=list(labellingToDo.objects.values('table_name').annotate(total=Count('table_name')))           
    labeledAtLeastOnce=list(labellingToDo.objects.all().filter(labeled__gt=0).values('table_name').annotate(labeledatleastOnce=Count('categ')))
    labeled=list(labellingToDo.objects.all().filter(labeled=nb_labellingtodo_bylabel).values('table_name').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbytable=pd.DataFrame(total)
    resbytable=resbytable.groupby('table_name').max().fillna(0).astype(int).reset_index().to_dict('records')

    total=list(labellingToDo.objects.all().values('table_name','categ').annotate(total=Count('categ')))            
    labeledAtLeastOnce=list(labellingToDo.objects.all().filter(labeled__gt=0).values('table_name','categ').annotate(labeledatleastOnce=Count('categ'))) 
    labeled=list(labellingToDo.objects.all().filter(labeled=nb_labellingtodo_bylabel).values('table_name','categ').annotate(labeled=Count('categ'))) 
    total.extend(labeledAtLeastOnce)
    total.extend(labeled)
    resbygroup=pd.DataFrame(total)
    resbygroup=resbygroup.groupby(['table_name', 'categ']).max().fillna(0).astype(int).reset_index().to_dict('records')  

    if request.method == "POST":
        if 'unknown' in request.POST:
            reinit=labellingDone.objects.filter(author=author).filter(unknown=True).all()
            reinit.delete()
            return HttpResponseRedirect(reverse('labelling_groupChoice'))
        if 'labellingbyhand' in request.POST:
            return HttpResponseRedirect(reverse('labellingbyhand_label'))
    return render(request, 'endpoints/labelling_final.html', {'resbytable':resbytable, 'resbygroup':resbygroup})
