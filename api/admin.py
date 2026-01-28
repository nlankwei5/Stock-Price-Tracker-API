from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display =[
        'stock', 
        'price',
        'timestamp'
    ]
