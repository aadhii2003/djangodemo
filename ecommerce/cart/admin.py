from django.contrib import admin

from cart.models import Cart

from cart.models import Orderdetails

from cart.models import Payment

from http import httpresponse

# Register your models here.
admin.site.register(Cart)
admin.site.register(Orderdetails)
admin.site.register(Payment)