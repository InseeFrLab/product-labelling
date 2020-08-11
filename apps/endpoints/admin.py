from django.contrib import admin
from apps.endpoints.models import labellingByHand, labellingDone

admin.site.register(labellingByHand)
admin.site.register(labellingDone)
