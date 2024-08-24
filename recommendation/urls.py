from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, InteractionViewSet,RecommendPostsView,RecommendPostsForUserView,CalculateView, GetRecommendPostView, ComputeThread

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'interactions', InteractionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recommend/<int:post_id>/', RecommendPostsView.as_view(), name='recommend-posts'),
    path('recommendForUser/<int:user_id>/', RecommendPostsForUserView.as_view(), name='recommend-posts-forUser'),
    path('newTrending/<int:post_id>/', CalculateView.as_view(),name="new-trending"),
    path('getRecommendedPosts',GetRecommendPostView.as_view(),name="get-recommendedPosts"),
    path('computeThread',ComputeThread.as_view(),name="compute-thread")
]
