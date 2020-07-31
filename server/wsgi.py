"""
WSGI config
"""

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
application = get_wsgi_application()

import inspect
from apps.ml.classifier.fasttext import FasttextClassifier

try:
    ft = FasttextClassifier()
    prediction=ft.compute_prediction({"label_in": 'cahier'})["predictions"]

except Exception as e:
    print("Exception while predicting,", str(e))
