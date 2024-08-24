from django.apps import AppConfig


class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendation'
    
    def ready(self):
        from data_loader import updater
        updater.start()