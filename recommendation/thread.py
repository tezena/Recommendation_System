from concurrent.futures import as_completed
from django_thread import ThreadPoolExecutor
from .models import *
from .serializers import *
from rest_framework.response import Response


def create_post(requestData):

    serializer=TestPostSerializer(data=requestData)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors, status=400)


def create_Interaction(requestData):
    serializer=TestInteractionSerializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)


def create_Recommend(requestData):
    serializer=TestPostRecommendSerializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)


