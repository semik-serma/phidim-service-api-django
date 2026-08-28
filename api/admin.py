from django.contrib import admin
from .models import Category,Service,Profile,Article,Comment,Reply,TotalLikesonComment,CrouselImages
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(Profile)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(TotalLikesonComment)
admin.site.register(CrouselImages)