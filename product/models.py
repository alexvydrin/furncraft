from django.conf import settings
from django.db import models
from django.utils import timezone


class Product(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    passport_link = models.CharField(max_length=200)
    site_link = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    price_calc = models.DecimalField(decimal_places=2, max_digits=10, default = None, null=True)
    price_doc = models.DecimalField(decimal_places=2, max_digits=10, default = None, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name
