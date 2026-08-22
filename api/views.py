from rest_framework import viewsets
from .serializers import CategorySerializer
from .models import Category,Service
# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()