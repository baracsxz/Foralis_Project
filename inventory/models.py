from django.db import models
from django.utils import timezone

CATEGORY_CHOICES = [
    ('Marine', 'Marine Solutions'),
    ('Industrial', 'Industrial Systems'),
    ('Engineering', 'Engineering Supplies'),
    ('Construction', 'Construction Materials'),
    ('Chemicals', 'Chemicals & Maintenance'),
]

UNIT_CHOICES = [
    ('pcs', 'Pieces'),
    ('pc', 'Piece'),
    ('kg', 'Kilograms'),
    ('m', 'Meters'),
    ('drum', 'Drums'),
    ('sheet', 'Sheet'),
    ('set', 'Set'),
    ('kit', 'Kit'),
    ('unit', 'Unit')
]

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, record_type, details):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        DeletionLog.objects.create(
            record_type=record_type,
            record_id=self.pk,
            display_name=str(self),
            details=details
        )

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

class Supplier(SoftDeleteModel, models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Material(SoftDeleteModel, models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=10, help_text="Alert when stock hits this level")

    def is_low_stock(self):
        return self.current_stock <= self.min_stock_level

    def __str__(self):
        status = " (LOW)" if self.is_low_stock() else ""
        return f"{self.name} - {self.current_stock} {self.unit}{status}"

class Movement(SoftDeleteModel, models.Model):
    TYPES = (('IN', 'Incoming/Received'), ('OUT', 'Outgoing/To Project'))
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=TYPES)
    quantity = models.PositiveIntegerField()
    project_site = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.is_deleted:
            if self.movement_type == 'IN':
                self.material.current_stock += self.quantity
            else:
                self.material.current_stock -= self.quantity
            self.material.save()
        super().save(*args, **kwargs)

class DeletionLog(models.Model):
    record_type = models.CharField(max_length=50)
    record_id = models.IntegerField()
    display_name = models.CharField(max_length=255)
    details = models.TextField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Archive/Delete Log'
        verbose_name_plural = 'System Trash Archive'

    def __str__(self):
        return f"{self.record_type}: {self.display_name}"