import pandas as pd
from django.core.management.base import BaseCommand
from recommendation.models import Post, Interaction
from recommendation.vectorization import build_tfidf_model, create_user_profiles
from recommendation.qdrant_helper import create_collections, upsert_post_vector, upsert_user_profile
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

class Command(BaseCommand):
    help = 'Load data from CSV and initialize vectorization'

    def handle(self, *args, **kwargs):
        """
        1. Load posts and interaction data from CSV
        2. Map the event type to the event strength:
           - Adds a new column `event_strength` to the interactions DataFrame based on the mapping.
        3. Build a TF-IDF model based on the posts data:
           - Creates a TF-IDF vector matrix for the posts content
        4. Create collections in the vector database:
        5. Upsert post vectors into the vector database:
           - Store post in Qdrant database, their id, and vector value
        6. Create user profile vectors based on interactions and post vectors:
           - Generates user profile vectors by aggregating interaction strengths with post vectors.
        7. Upsert user profile vectors into the vector database:
           - Store user interaction vector in database according to user id
        8. Print a success message upon completion:
        """

        try:
            posts_csv_path = os.path.join('recommendation', 'posts3.csv')
            interactions_csv_path = os.path.join('recommendation', 'interaction.csv')

            # Load posts data
            posts_df = pd.read_csv(posts_csv_path)
            posts_df = posts_df.head(50)

            # Load interactions data
            interactions_df = pd.read_csv(interactions_csv_path)
            event_type = {
                'view': 1,
                'dislike': -3,
                'react-positive': 2,
                'best_time_spent': 3,
                'like': 5,
                'react-negative': -2,
                'comment-best-positive': 7,
                'comment-average-positive': 6,
                'average_time_spent': 3,
                'good_time_spent': 2,
                'comment-average-negative': -2,
                'comment-best-negative': -1
            }

            # Create event_strength
            interactions_df['event_strength'] = interactions_df['event_type'].map(event_type)

            # Populate the Post model
            Post.objects.all().delete()
            for index, row in posts_df.iterrows():
                Post.objects.create(content_id=row['content_id'], title=row['title'], content=row['content'])

            # Populate the Interaction model
            Interaction.objects.all().delete()
            for index, row in interactions_df.iterrows():
                Interaction.objects.create(
                    user_id=row['user__user_id'],
                    post_content_id=Post.objects.get(content_id=row['post__content_id']),
                    event_strength=row['event_strength']
                )

            vectorizer, tfidf_matrix = build_tfidf_model(posts_df)
            print(tfidf_matrix.shape[1])
            create_collections(tfidf_matrix.shape[1], "posts")
            create_collections(tfidf_matrix.shape[1], "user_profiles")

            batch_size = 25
            points = []
            for idx, row in posts_df.iterrows():
                vector = tfidf_matrix[idx].toarray().flatten().tolist()
                point = PointStruct(id=row['content_id'], vector=vector, payload={"type": "posts"})
                points.append(point)

                if len(points) >= batch_size:
                    upsert_post_vector(points)
                    points = []

            if points:
                upsert_post_vector(points)

            user_profile_vector = create_user_profiles(interactions_df, tfidf_matrix, posts_df['content_id'].tolist())

            points = []
            for user_id, vector in user_profile_vector.items():
                vector = vector.flatten().tolist()
                point = PointStruct(id=user_id, vector=vector, payload={"type": "user_profile"})
                points.append(point)

                if len(points) >= batch_size:
                    upsert_user_profile(points)
                    points = []

            if points:
                upsert_user_profile(points)

            print('Successfully loaded data and initialized vectorization')

        except Exception as e:
            raise Exception(f"Failed to load data: {e}")
