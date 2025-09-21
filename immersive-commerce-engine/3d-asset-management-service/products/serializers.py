from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'model_3d_url', 'ar_enabled', 'created_at', 'updated_at']
