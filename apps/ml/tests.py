from django.test import TestCase

from apps.ml.classifier.fasttext import FasttextClassifier
import inspect
from apps.ml.registry import MLRegistry

class MLTests(TestCase):
    def test_ft_algorithm(self):
        input_data = {
            "libelle": "cahier"
        }
        my_alg = FasttextClassifier()
        response = my_alg.compute_prediction(input_data)
        self.assertEqual('OK', response['status'])

    def test_registry(self):
        registry = MLRegistry()
        self.assertEqual(len(registry.endpoints), 0)
        endpoint_name = "classifier"
        algorithm_object = FasttextClassifier()
        algorithm_name = "fasttext"
        algorithm_status = "production"
        algorithm_version = "0.0.1"
        algorithm_owner = ""
        algorithm_description = "Fasttext with simple pre-processing"
        algorithm_code = inspect.getsource(FasttextClassifier)
        # add to registry
        registry.add_algorithm(endpoint_name, algorithm_object, algorithm_name,
                    algorithm_status, algorithm_version, algorithm_owner,
                    algorithm_description, algorithm_code)
        # there should be one endpoint available
        #self.assertEqual(len(registry.endpoints), 1)
