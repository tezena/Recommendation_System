from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Post, Interaction , RecommendedPost
from .serializers import PostSerializer, InteractionSerializer
from .vectorization import build_tfidf_model, create_user_profiles
from .qdrant_helper import client
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from rest_framework.views import APIView
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
from .postgres_helper import bulk_create_recommended_posts

from .serializers import RecommendedPostSerializer

from concurrent.futures import as_completed
from django_thread import ThreadPoolExecutor
from .thread import *
import concurrent.futures

from django.db import connections




"""
.\Scripts\Activate.ps1

"""


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer


def fetch_post_vector(post_id):
    result = client.retrieve(
        collection_name="posts",
        ids=[int(post_id)]
    )
    if result['status'] == 'ok' and result['result']:
        return np.array(result['result'][0]['vector'])
    else:
        raise ValueError("Vector not found for content_id: {}".format(post_id))



# recommendation/views.py



class RecommendPostsView(APIView):
    def get(self, request, post_id, *args, **kwargs):
        try:
            # Fetch all post vectors
         
            all_post_vectors_response = client.scroll(
                collection_name="posts",
                scroll_filter=None,
                with_vectors=True,
                limit=10000
               ),
              
            
             
            all_post_vectors=all_post_vectors_response[0]
            all_post_vectors=all_post_vectors[0]
            # print("All post vectors fetched:", all_post_vectors)

            post_ids = [record.id for record in all_post_vectors]
            post_vectors = [record.vector for record in all_post_vectors]
         
           
            # Get the vector for the specified post_id
            post_index = post_ids.index(post_id)
            post_vector = post_vectors[post_index]
           


            # Filter out the post vector from the list of all vectors
            indices_to_keep = [i for i, pid in enumerate(post_ids) if pid != int(post_id)]
            filtered_post_ids = [post_ids[i] for i in indices_to_keep]
            filtered_post_vectors = [post_vectors[i] for i in indices_to_keep]

            # Debugging logs
            print("Filtered Post IDs:", filtered_post_ids)
            print("Filtered Post Vectors Shape:", len(filtered_post_vectors))

            # Calculate cosine similarity
            cosine_similarities = cosine_similarity([post_vector], filtered_post_vectors).flatten()

            # Get top-N similar posts
            top_n = 10
            similar_indices = cosine_similarities.argsort()[-top_n:][::-1]
            similar_posts = [(filtered_post_ids[i], cosine_similarities[i]) for i in similar_indices]

            # Fetch the actual posts from the database
            recommended_posts = Post.objects.filter(content_id__in=[post[0] for post in similar_posts])
            serializer = PostSerializer(recommended_posts, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Detailed error logging
            print("Error occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RecommendPostsForUserView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Fetch the user's profile vector
            print('called')
            user_profile_vector = get_user_profile_vector(user_id)  # Implement this function

            if user_profile_vector is None:
                return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
         
            final_result = client.search(
                collection_name="posts",
                query_vector=user_profile_vector,
                limit=1000,
            ) 
            
            print(final_result)
            
            post_ids=[record.id for record in final_result]
            print(post_ids)
            
            recommended_posts = Post.objects.filter(content_id__in=[id for id in post_ids])
            serializer = PostSerializer(recommended_posts, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Detailed error logging
            print("Error occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Function to get the user profile vector
def get_user_profile_vector(user_id):
 
   
    try:
       
        result = client.retrieve(
        collection_name="user_profiles",
        ids=[int(user_id)],
        with_vectors=True
       
        )

        user_profile_vector=None
        
        if result:
           user_profile_vector=[record.vector for record  in result if record.id==user_id][0]
        else:
           raise ValueError("Vector not found for content_id: {}".format(post_id))
          
        return user_profile_vector
       
    except Exception as e:
        print("Error fetching user profile vector:", str(e))
        return None







class CalculateView(APIView):
    def get(self, request, post_id, *args, **kwargs):
        try:
            # Fetch the user's profile vector
            print('called')
            serializer=RecommendedPostSerializer()

            trending_vector=get_single_vector(post_id)


            if trending_vector is None:
                return Response({"error": "trending  not found"}, status=status.HTTP_404_NOT_FOUND)
            
         
            similarity_result = client.search(
                collection_name="posts",
                query_vector=trending_vector,
                limit=1000,
            ) 
            
            print(similarity_result)
            
            # post_ids=[record.id for record in final_result]
            # post_scores=[record.score for record in final_result]
            
            serializer.bulk_create_recommended_posts(similarity_result,batch_size=50)

            return Response({"status":"success"})
            
            # recommended_posts = Post.objects.filter(content_id__in=[id for id in post_ids])
            # serializer = PostSerializer(recommended_posts, many=True)
           
        except Exception as e:
            # Detailed error logging
            print("Error occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetRecommendPostView(APIView):
     def  get(self, request, *args, **kwargs):
          try:
             recommended_posts = RecommendedPost.objects.all().values('content_id','similarity_score','recommendedPost_id')
             recommended_posts_list = list(recommended_posts)
             return Response(recommended_posts_list)
          except Exception as e:
              print("Error occurred:", str(e))
              return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                


def get_single_vector(post_id):

    all_post_vectors_response = client.scroll(
                collection_name="posts",
                scroll_filter=None,
                with_vectors=True,
                limit=10000
               ),
              
            
             
    all_post_vectors=all_post_vectors_response[0]
    all_post_vectors=all_post_vectors[0]
            # print("All post vectors fetched:", all_post_vectors)

    post_ids = [record.id for record in all_post_vectors]
    post_vectors = [record.vector for record in all_post_vectors]
         
           
            # Get the vector for the specified post_id
    post_index = post_ids.index(post_id)
    post_vector = post_vectors[post_index]

    return post_vector



def on_done(future):
    # Because each thread has a connection, so here you can call close_all() to close all connections under this thread name.
        connections.close_all()

class ComputeThread(APIView):
    def post(self,request,*args, **kwargs):
       

        try:
            data=request.data
            post_data = data.get('post_data', {})
            interaction_data = data.get('interaction_data', {})
            recommend_data = data.get('recommend_data', {})
             
            
            executor = ThreadPoolExecutor()



            with concurrent.futures.ThreadPoolExecutor() as executor:
                tasks = [
                    executor.submit(lambda:create_post(requestData=post_data)),
                    executor.submit(lambda:create_Interaction(requestData=interaction_data)),
                    executor.submit(lambda:create_Recommend(requestData=recommend_data))
                ]

                for task in tasks:
                     task.add_done_callback(on_done)
                results = [task.result() for task in tasks]

   
            # query_one=executor.submit(lambda:create_post(requestData=post_data))
            # query_two=executor.submit(lambda:create_Interaction(requestData=interaction_data))
            # query_three=executor.submit(lambda:create_Recommend(requestData=recommend_data))
            
            # results=[]

            # for future in as_completed([query_one,query_two,query_three]):
            #     try:
            #         result=future.result()
            #         results.append(result)
            #     except Exception as e:
            #         print(f"Error occured {e}")

            

            for result in results:
                print(result)
            
            return Response({"status":"success"})

        except Exception as e:
            print(f"something wrong {e}")
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
