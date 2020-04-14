"""
WSGI config for gettingstarted project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
application = get_wsgi_application()

# ML registry
import inspect
from apps.ml.registry import MLRegistry
from apps.ml.classifier.fasttext import FasttextClassifier

try:
    registry = MLRegistry() # create ML registry
    ft = FasttextClassifier()
    # add to ML registry
    registry.add_algorithm(endpoint_name="classifier",
                            algorithm_object=ft,
                            algorithm_name="fasttext",
                            algorithm_status="production",
                            algorithm_version="0.0.1",
                            owner="",
                            algorithm_description="Fasttext with simple pre-processing",
                            algorithm_code=inspect.getsource(FasttextClassifier))

except Exception as e:
    print("Exception while loading the algorithms to the registry,", str(e))
