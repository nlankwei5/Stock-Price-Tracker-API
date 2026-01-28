from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r"Stock", StockViewset, basename="stock")



url_patterns = router.urls