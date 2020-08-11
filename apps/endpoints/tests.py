from django.test import TestCase
from rest_framework.test import APIClient

class EndpointTests(TestCase):

    def test_predict_view(self):
        client = APIClient()
        input_data = "name"
        test_url = "/labellingbyhand/author"
        response = client.post(test_url, input_data)
        self.assertEqual(response.status_code, 200)

