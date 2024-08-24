from django.test import Client, TestCase
from rest_framework import status
from django.test import TestCase
from .models import Test_Post, Test_Interaction, Test_Recommend
from .serializers import TestPostSerializer, TestInteractionSerializer, TestPostRecommendSerializer
from .thread import *
import json



# Create your tests here.

class TestPostFunctions(TestCase):
    def test_create_post_valid_data(self):
        # Test valid data
        valid_data = {
            "post_title": "Test Title",
            "post_content": "Test Content"
        }
        response = create_post(valid_data)
        self.assertEqual(response.status_code, 201)

    def test_create_interaction_valid_data(self):
        # Test valid data
        valid_data = {
            "user_id": 2,
            "post_content_id": "2",
            "event_strength": 0.5
        }
        response = create_Interaction(valid_data)
        self.assertEqual(response.status_code, 201)

    def test_create_recommend_valid_data(self):
        # Test valid data
        valid_data = {
            "content_id": "Test content_id 2"
        }
        response = create_Recommend(valid_data)
        self.assertEqual(response.status_code, 201)

# class TestPostFunctionsErrorHandling(TestCase):
#     def test_create_post_invalid_data(self):
#         # Test invalid data
#         invalid_data = {
#             "post_title": "",  # Empty title
#             "post_content": "Test Content"
#         }
#         response = create_post(invalid_data)
#         self.assertEqual(response.status_code, 400)



class TestComputeThreadView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_compute_thread_post(self):
        url = 'http://127.0.0.1:8000/api/computeThread'  


        response = self.client.post(
        path=url,
        data=json.dumps({
             "recommend_data" : {
            "content_id": "Test content_id 4"
        },
           "interaction_data": {
            "user_id": 4,
            "post_content_id":"4",
            "event_strength": 0.5
        },
        "post_data":{
            "post_title": "Test Title",
            "post_content": "Test Content"
        }
        }),
        content_type='application/json'
    )
       
        # response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')