from django.apps import AppConfig


class VisionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vision'

    def ready(self):
        import vision.signals
