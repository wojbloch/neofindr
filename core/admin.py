from django.contrib import admin
from django.apps import apps

admin.site.site_header = "neofindr API administration"
admin.site.site_title = "neofindr API admin"
admin.site.index_title = "neo API"

models = apps.get_models()

for model in models:
    if model._meta.app_label in [
        "core",
        "auth",
        "contenttypes",
        "sessions",
        "admin",
        "sites",
    ]:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            continue
