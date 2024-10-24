from django.contrib import admin
from .models import *

admin.site.register(Payment)
admin.site.register(PaymentType)
admin.site.register(Validation)
admin.site.register(Bank)