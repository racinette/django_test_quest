from django.contrib import admin

from .models import Item, Order, Discount, Tax, OrderItem

# Register your models here.
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(Tax)
admin.site.register(OrderItem)
