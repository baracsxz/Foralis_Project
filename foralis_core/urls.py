from django.contrib import admin
from django.urls import path

# FIXED: fully stripped old structural injection overrides that break container height calculations
admin.site.site_header = "Foralis Admin Portal"
admin.site.site_title = "Foralis Admin Portal"
admin.site.index_title = "Foralis Inventory Management"

urlpatterns = [
    path('admin/', admin.site.urls),
]