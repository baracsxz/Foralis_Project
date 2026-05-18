from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from django.urls import reverse
from .models import Material, Movement, Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email', 'edit_button', 'delete_button')
    search_fields = ('name',)

    def edit_button(self, obj):
        url = reverse('admin:inventory_supplier_change', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>', url)
    edit_button.short_description = 'Edit supplier'

    def delete_button(self, obj):
        url = reverse('admin:inventory_supplier_delete', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #ba2121; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Delete</a>', url)
    delete_button.short_description = 'Delete supplier'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'current_stock_status',
        'unit',
        'unit_cost_display',
        'stock_value_display',
        'supplier',
        'edit_button',
        'delete_button'
    )
    search_fields = ('name', 'supplier__name', 'category')
    list_filter = ('category', 'unit', 'supplier')

    def current_stock_status(self, obj):
        if obj.is_low_stock():
            return format_html(
                '<span style="color: red; font-weight: bold;">{} (LOW STOCK)</span>',
                obj.current_stock
            )
        return obj.current_stock
    current_stock_status.short_description = 'Current Stock'

    def unit_cost_display(self, obj):
        return f"₱{obj.unit_cost:,.2f}"
    unit_cost_display.short_description = 'Unit Cost'

    def stock_value_display(self, obj):
        value = obj.current_stock * obj.unit_cost
        formatted_value = f"₱{value:,.2f}"
        return format_html('<b style="color: #28a745;">{}</b>', formatted_value)
    stock_value_display.short_description = 'Stock Value (PHP)'

    def edit_button(self, obj):
        url = reverse('admin:inventory_material_change', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>', url)
    edit_button.short_description = 'Edit item'

    def delete_button(self, obj):
        url = reverse('admin:inventory_material_delete', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #ba2121; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Delete</a>', url)
    delete_button.short_description = 'Delete item'

    def changelist_view(self, request, extra_context=None):
        total_value = Material.objects.aggregate(
            total=Sum(F('current_stock') * F('unit_cost'), output_field=DecimalField())
        )['total'] or 0
        extra_context = extra_context or {}
        extra_context['total_inventory_value'] = f"₱{total_value:,.2f}"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('formatted_date', 'material', 'movement_type', 'quantity', 'project_site', 'edit_button', 'delete_button')
    list_filter = ('movement_type', 'date', 'project_site')
    search_fields = ('material__name', 'project_site')
    date_hierarchy = 'date'

    def formatted_date(self, obj):
        local_date = timezone.localtime(obj.date)
        return local_date.strftime("%b %d, %Y, %I:%M %p")
    formatted_date.short_description = 'Date & Time (PHT)'
    formatted_date.admin_order_field = 'date'

    def edit_button(self, obj):
        url = reverse('admin:inventory_movement_change', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>', url)
    edit_button.short_description = 'Edit log'

    def delete_button(self, obj):
        url = reverse('admin:inventory_movement_delete', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #ba2121; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Delete</a>', url)
    delete_button.short_description = 'Delete log'