from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    create_uid = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_%(class)s", on_delete=models.SET_NULL, null=True, blank=True)
    write_uid = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="modified_%(class)s", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

class Setting(BaseModel):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name} : {self.value}"


class Zone(BaseModel):
    designation = models.CharField(max_length=50)
    address = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.designation

class Objective(BaseModel):
    zone = models.ForeignKey(Zone, related_name='objectives', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    month = models.DateField()

    class Meta:
        unique_together = ('zone', 'month') 
    
    def __str__(self):
        return f"Objectif de la zone {self.zone.designation} pour le mois de {self.month.strftime('%B %Y')}"

class User(BaseModel, AbstractUser):
    ROLE_CHOICES = [
        ('Nouveau', 'Nouveau'),
        ('Commercial', 'Commercial'),
        ('Zone Manageur', 'Zone Manageur'),
        ('Back Office', 'Back Office'),
        ('Observateur', 'Observateur'),
        ('Admin', 'Admin')
    ]

    fullname = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, max_length=30)
    zones = models.ManyToManyField(Zone, related_name='users', blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname
    
    def has_admin(self):
        return self.role == 'Admin'
    
    def has_backoffice(self):
        return self.role == 'Back Office'
    
    def has_commercial(self):
        return self.role in ['Commercial', 'Zone Manageur']
    
    def has_obs(self):
        return self.role == 'Observateur'

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
