from django.db import models

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

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Material(models.Model):
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

class Movement(models.Model):
    TYPES = (('IN', 'Incoming/Received'), ('OUT', 'Outgoing/To Project'))
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=TYPES)
    quantity = models.PositiveIntegerField()
    project_site = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.movement_type == 'IN':
            self.material.current_stock += self.quantity
        else:
            self.material.current_stock -= self.quantity
        self.material.save()
        super().save(*args, **kwargs)