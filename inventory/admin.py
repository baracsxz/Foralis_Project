from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect
from .models import Material, Movement, Supplier, DeletionLog


class ActiveAdmin(admin.ModelAdmin):
    exclude = ('is_deleted', 'deleted_at')
    actions = ['delete_selected_archive']

    def get_queryset(self, request):
        return self.model.objects.filter(is_deleted=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_selected_archive(self, request, queryset):
        count = 0
        for obj in queryset:
            record_type = obj.__class__.__name__
            if record_type == 'Movement':
                details = f"type: {obj.get_movement_type_display()}, qty: {obj.quantity}, site: {obj.project_site}"
            elif record_type == 'Material':
                details = f"cat: {obj.get_category_display()}, stock: {obj.current_stock} {obj.unit}"
            else:
                details = f"contact: {obj.contact_person}, ph: {obj.phone_number}"

            obj.soft_delete(record_type=record_type, details=details)
            count += 1

        messages.warning(request, f"successfully archived {count} selected records to the delete log.")

    delete_selected_archive.short_description = "Delete selected items (Archive)"

    def delete_model(self, request, obj):
        record_type = obj.__class__.__name__
        if record_type == 'Movement':
            details = f"type: {obj.get_movement_type_display()}, qty: {obj.quantity}, site: {obj.project_site}"
        elif record_type == 'Material':
            details = f"cat: {obj.get_category_display()}, stock: {obj.current_stock} {obj.unit}"
        else:
            details = f"contact: {obj.contact_person}, ph: {obj.phone_number}"

        obj.soft_delete(record_type=record_type, details=details)
        messages.warning(request,
                         f"CRITICAL EVENT LOG: A delete operation occurred on {timezone.now().strftime('%b %d, %Y, %I:%M %p')} PHT.")


@admin.register(Supplier)
class SupplierAdmin(ActiveAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email', 'edit_button')
    search_fields = ('name',)

    def edit_button(self, obj):
        url = reverse('admin:inventory_supplier_change', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>',
            url)

    edit_button.short_description = 'Edit'


@admin.register(Material)
class MaterialAdmin(ActiveAdmin):
    list_display = ('name', 'category', 'current_stock_status', 'unit', 'unit_cost_display', 'stock_value_display',
                    'supplier', 'edit_button')
    search_fields = ('name', 'supplier__name', 'category')
    list_filter = ('category', 'unit', 'supplier')

    def current_stock_status(self, obj):
        if obj.is_low_stock():
            return format_html('<span style="color: red; font-weight: bold;">{} (LOW STOCK)</span>', obj.current_stock)
        return obj.current_stock

    current_stock_status.short_description = 'Current Stock'

    def unit_cost_display(self, obj):
        return f"₱{obj.unit_cost:,.2f}"

    unit_cost_display.short_description = 'Unit Cost'

    def stock_value_display(self, obj):
        value = obj.current_stock * obj.unit_cost
        return f"₱{value:,.2f}"

    stock_value_display.short_description = 'Stock Value'

    def edit_button(self, obj):
        url = reverse('admin:inventory_material_change', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>',
            url)

    edit_button.short_description = 'Edit'

    def changelist_view(self, request, extra_context=None):
        total_value = Material.objects.filter(is_deleted=False).aggregate(
            total=Sum(F('current_stock') * F('unit_cost'), output_field=DecimalField())
        )['total'] or 0
        extra_context = extra_context or {}
        extra_context['total_inventory_value'] = f"₱{total_value:,.2f}"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Movement)
class MovementAdmin(ActiveAdmin):
    list_display = ('formatted_date', 'material', 'movement_type', 'quantity', 'project_site', 'edit_button')
    list_filter = ('movement_type', 'date', 'project_site')
    search_fields = ('material__name', 'project_site')
    date_hierarchy = 'date'

    def formatted_date(self, obj):
        return timezone.localtime(obj.date).strftime("%b %d, %Y, %I:%M %p")

    formatted_date.short_description = 'Date & Time'

    def edit_button(self, obj):
        url = reverse('admin:inventory_movement_change', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color: #264b5d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; text-decoration: none;">Edit</a>',
            url)

    edit_button.short_description = 'Edit'


@admin.register(DeletionLog)
class DeletionLogAdmin(admin.ModelAdmin):
    list_display = ('formatted_date', 'record_type', 'display_name', 'details', 'actions_display')
    list_filter = ('record_type', 'deleted_at')
    search_fields = ('display_name', 'details')

    def has_add_permission(self, request):
        return False

    def formatted_date(self, obj):
        return timezone.localtime(obj.deleted_at).strftime("%b %d, %Y, %I:%M %p")

    formatted_date.short_description = 'Date & Time (PHT)'

    def actions_display(self, obj):
        restore_url = reverse('admin:global-restore', args=[obj.pk])
        purge_url = reverse('admin:global-purge', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color: #198754; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; margin-right: 5px; font-weight: bold;">Restore Data 📤</a>'
            '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-weight: bold;">Permanently Purge</a>',
            restore_url, purge_url
        )

    actions_display.short_description = 'Actions'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        return [
            path('<path:object_id>/restore/', self.admin_site.admin_view(self.restore_view), name='global-restore'),
            path('<path:object_id>/purge/', self.admin_site.admin_view(self.purge_view), name='global-purge'),
        ] + urls

    def restore_view(self, request, object_id):
        log = self.get_object(request, object_id)
        if log:
            from django.apps import apps
            model = apps.get_model('inventory', log.record_type)
            item = model.objects.filter(pk=log.record_id).first()
            if item:
                item.restore()
            log.delete()
            messages.success(request, f"Successfully restored {log.display_name} data record.")
        return redirect('admin:inventory_deletionlog_changelist')

    def purge_view(self, request, object_id):
        log = self.get_object(request, object_id)
        if log:
            from django.apps import apps
            model = apps.get_model('inventory', log.record_type)
            model.objects.filter(pk=log.record_id).delete()
            log.delete()
            messages.error(request, f"Permanently purged record log from database.")
        return redirect('admin:inventory_deletionlog_changelist')