from django.contrib import admin

from cart.models import Cart

from cart.models import Order_details,payment
from http import HttpResponse
admin.site.register(Cart)
admin.site.register(Order_details)
admin.site.register(payment)
