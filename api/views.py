from rest_framework import viewsets
from .serializers import * 
from .models import * 


class StockViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


