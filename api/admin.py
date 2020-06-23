from django.contrib import admin
from .models import CustomUser, Post, Adset, AdsetOrignal,Adset_updte_hours


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Adset)
admin.site.register(AdsetOrignal)
admin.site.register(Adset_updte_hours)