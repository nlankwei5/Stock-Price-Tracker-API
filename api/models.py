from django.db import models

# Create your models here.


class Stock(models.Model):
    stock = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    timestamp = models.DateTimeField(db_index=True, auto_now_add=True)


    class Meta:
        indexes =[
            models.Index(fields=['timestamp', 'stock']),
        ]

