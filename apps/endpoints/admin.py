from django.contrib import admin
from apps.endpoints.models import LabelingByHand, LabelingDone

admin.site.register(LabelingByHand)
admin.site.register(LabelingDone)
