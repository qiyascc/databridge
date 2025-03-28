from django.apps import AppConfig


class LcwaikikiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lcwaikiki"

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            from lcwaikiki.schedulers import TaskScheduler
            
            scheduler = TaskScheduler()
            
            scheduler.add_task('run_spider sitemap', interval_hours=6, initial_delay_minutes=1)
            scheduler.add_task('run_spider location', interval_hours=18, initial_delay_minutes=4)            
            scheduler.add_task('run_spider product', interval_hours=18, initial_delay_minutes=4)            

            scheduler.start()
