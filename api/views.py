from rest_framework import viewsets, status
from rest_framework.decorators import action
from .serializers import * 
from .models import * 
from .task import ingest_stock_prices
from rest_framework.response import Response


class StockViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    @action(detail=False, methods=['GET'])
    def call_api(self, request):
        ingest_stock_prices.delay()

        return Response (
            {"status": "Stock prices enqueued"},
            status=status.HTTP_202_ACCEPTED
        )