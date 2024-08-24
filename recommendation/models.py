from django.db import models

# Create your models here.


class Post(models.Model):
    content_id = models.IntegerField(primary_key=True)
    title = models.TextField()
    content = models.TextField()
    post_type=models.TextField(null=True,blank=True)
    post_type_format=models.TextField(null=True,blank=True)

class Interaction(models.Model):
    user_id = models.IntegerField()
    post_content_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    event_strength = models.FloatField()



class RecommendedPost(models.Model):
    recommendedPost_id=models.AutoField(primary_key=True)
    content_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    similarity_score=models.FloatField(null=True,blank=True)






class Test_Post(models.Model):
    post_id=models.AutoField(primary_key=True)
    post_title=models.TextField()
    post_content=models.TextField()


class Test_Interaction(models.Model):
    user_id = models.IntegerField()
    post_content_id = models.TextField()
    event_strength = models.FloatField()

class Test_Recommend(models.Model):
    recommendedPost_id=models.AutoField(primary_key=True)
    content_id = models.TextField()
   

    

