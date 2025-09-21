from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    model_3d_url = models.URLField(max_length=500)
    ar_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
