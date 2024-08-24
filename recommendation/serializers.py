from rest_framework import serializers

from django.db import transaction
from .models import Post, Interaction, RecommendedPost,Test_Interaction,Test_Post,Test_Recommend

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'



class TestPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test_Post
        fields='__all__'

class TestInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test_Interaction
        fields='__all__'

class TestPostRecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test_Recommend
        fields='__all__'
    


class RecommendedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPost
        fields = ['content_id', 'similarity_score']

    def bulk_create_recommended_posts(self, similarity_result, batch_size=100):

        if RecommendedPost.objects.exists():
            with transaction.atomic():
                RecommendedPost.objects.all().delete()

     
        recommended_post_instances = []

        for record in similarity_result:
            post_instance= Post.objects.get(content_id=record.id)

            recommended_post_instances.append(
                RecommendedPost(content_id=post_instance, similarity_score=record.score)
            )

            if len(recommended_post_instances) >= batch_size:
                with transaction.atomic():
                    RecommendedPost.objects.bulk_create(recommended_post_instances)
                recommended_post_instances = []

   
        if recommended_post_instances:
            with transaction.atomic():
                RecommendedPost.objects.bulk_create(recommended_post_instances)

