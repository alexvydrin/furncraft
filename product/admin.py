from django.contrib import admin
from .models import Product, Cost, Calculation, Settings

admin.site.register(Product)
admin.site.register(Cost)
admin.site.register(Calculation)
admin.site.register(Settings)
