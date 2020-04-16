from django.test import TestCase

from apps.ml.classifier.fasttext import FasttextClassifier
import inspect

class MLTests(TestCase):
    def test_ft_algorithm(self):
        input_data = {
            "libelle": "cahier"
        }
        my_alg = FasttextClassifier()
        response = my_alg.compute_prediction(input_data)
        self.assertEqual('OK', response['status'])


