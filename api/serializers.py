from rest_framework import serializers
from .models import * 


class StockSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Stock
        fields = ['id', 'stock', 'price', 'timestamp']
