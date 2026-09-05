from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views import (CategoryViewSet,
                       ServiceViewSet,
                       TechnicianRegisterAPIView,
                       UserProfileRetrieveView,
                       ProfileServiceAPIView,
                       ArticleModelViewSet,
                       CommentModelViewSet,
                       AnnouncementBannerViewSet,
                       ReplyViewSet,
                       LikesOnCommentViewSet,
                       CrouselImagesViewSet,
                       )
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'articles', ArticleModelViewSet, basename='article')
router.register(r'comments', CommentModelViewSet, basename='comment')
router.register(r'announcements', AnnouncementBannerViewSet, basename='announcement')
router.register(r'replies',ReplyViewSet,basename='reply')
router.register(r'likes',LikesOnCommentViewSet,basename='like')
router.register(r'crousel-images',CrouselImagesViewSet,basename='crousel-image')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "technicians/register/",
        TechnicianRegisterAPIView.as_view(),
        name="technician-register"
    ),
     path(
            "userprofile/",
            UserProfileRetrieveView.as_view(),
            name="user-profile-view"
        ),
         path(
                    "profileservice/",
                    ProfileServiceAPIView.as_view(),
                    name="profileservice"
                ),
]+router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
