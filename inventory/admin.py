from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField
from .models import Material, Movement


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'current_stock_status',
        'unit',
        'unit_cost_display',
        'stock_value_display',
        'supplier'
    )
    search_fields = ('name', 'supplier', 'category')
    list_filter = ('category', 'unit', 'supplier')

    def current_stock_status(self, obj):
        if obj.is_low_stock():
            return format_html(
                '<span style="color: red; font-weight: bold;">{} (LOW STOCK)</span>',
                obj.current_stock
            )
        return obj.current_stock

    current_stock_status.short_description = 'Current Stock'

    # FIXED: Format the number FIRST, then return it
    def unit_cost_display(self, obj):
        return f"₱{obj.unit_cost:,.2f}"

    unit_cost_display.short_description = 'Unit Cost'

    # FIXED: Calculate value first, then wrap in format_html
    def stock_value_display(self, obj):
        value = obj.current_stock * obj.unit_cost
        formatted_value = f"₱{value:,.2f}"
        return format_html('<b style="color: #28a745;">{}</b>', formatted_value)

    stock_value_display.short_description = 'Stock Value (PHP)'

    def changelist_view(self, request, extra_context=None):
        total_value = Material.objects.aggregate(
            total=Sum(F('current_stock') * F('unit_cost'), output_field=DecimalField())
        )['total'] or 0

        extra_context = extra_context or {}
        # FIXED: Pass a simple string to the context
        extra_context['total_inventory_value'] = f"₱{total_value:,.2f}"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('date', 'material', 'movement_type', 'quantity', 'project_site')
    list_filter = ('movement_type', 'date', 'project_site')
    search_fields = ('material__name', 'project_site')
    date_hierarchy = 'date'
