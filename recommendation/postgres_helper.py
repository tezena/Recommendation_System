from django.db import transaction
from .models import Post, RecommendedPost

BATCH_SIZE = 50

def bulk_create_recommended_posts(similarity_result):

    recommended_posts = Post.objects.filter(content_id__in=post_ids)

    if RecommendedPost.objects.exists():
        with transaction.atomic():
            RecommendedPost.objects.all().delete()

    recommended_post_instances = []
    
    for recored in similarity_result:
        recommended_post_instances.append(
            RecommendedPost(content_id=recored.id,similarity_score=recored.score)
        )

    # for post in recommended_posts:
    #     recommended_post_instances.append(
    #         RecommendedPost(content_id=post.content_id, title=post.title, content=post.content,post_type=post.post_type,post_type_format=post.post_type_format)
    #     )
        
        if len(recommended_post_instances) >= BATCH_SIZE:
            with transaction.atomic():
                RecommendedPost.objects.bulk_create(recommended_post_instances)
            recommended_post_instances = []
    

    print("posts stored successfully")

    if recommended_post_instances:
        with transaction.atomic():
            RecommendedPost.objects.bulk_create(recommended_post_instances)