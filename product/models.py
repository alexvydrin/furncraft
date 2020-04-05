from django.conf import settings
from django.db import models
from django.utils import timezone


class Product(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, unique=True)
    passport_link = models.CharField(blank=True, max_length=200, default="")
    site_link = models.CharField(blank=True, max_length=200, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    price_calc = models.DecimalField(blank=True, decimal_places=2, max_digits=10, default=None, null=True)
    price_doc = models.DecimalField(blank=True, decimal_places=2, max_digits=10, default=None, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Cost(models.Model):
    name = models.CharField(max_length=50, unique=True)
    sort = models.PositiveIntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    waste_percent = models.FloatField(blank=True, null=True)
    description = models.CharField(blank=True, max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
