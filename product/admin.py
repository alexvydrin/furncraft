from django.contrib import admin
from .models import Product, Cost, Calculation

admin.site.register(Product)
admin.site.register(Cost)
admin.site.register(Calculation)