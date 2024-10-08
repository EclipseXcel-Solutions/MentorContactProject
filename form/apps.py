from django.apps import AppConfig


class FormConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'form'

    def ready(self) -> None:
        import form.signals
        return super().ready()
