from rest_framework import viewsets
from .serializers import * 
from .models import * 


class StockViewset(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


