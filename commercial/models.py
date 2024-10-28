from django.db import models
from account.models import *
from django.template.defaultfilters import slugify
from PIL import Image as PILImage
import os

STATE_PAYMENT = [
    ('Brouillon', 'Brouillon'),
    ('Confirmé', 'Confirmé'),
    ('Validé', 'Validé'),
    ('Refusé', 'Refusé'),
    ('Annulé', 'Annulé'),
]

class Bank(BaseModel):
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.designation
    
class PaymentType(BaseModel):
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.designation

def get_check_image_filename(instance, filename):
    title = str(instance.id).zfill(4)
    slug = slugify(title)
    return f"images/check/{slug}-{filename}"
    
class Payment(BaseModel):

    commercial = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    client = models.CharField(max_length=255)
    client_id = models.IntegerField()
    payer = models.CharField(max_length=255, blank=True, null=True)
    payer_id = models.IntegerField(blank=True, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='payments')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='payments')
    check_image = models.ImageField(upload_to=get_check_image_filename, verbose_name='Check Image', blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    ref = models.CharField(max_length=7, blank=True, null=True)
    observation = models.TextField(null=True, blank=True)
    date = models.DateField()
    date_depot = models.DateField()
    state = models.CharField(choices=STATE_PAYMENT, max_length=40)
    
    def validations(self):
        return self.validation_set.all()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.check_image and os.path.exists(self.check_image.path):
            img = PILImage.open(self.check_image.path)
            max_size = (1280, 720)
            img.thumbnail(max_size, PILImage.LANCZOS)
            img.save(self.check_image.path, quality=50, optimize=True)

    def __str__(self):
        return f"Payment ID: {str(self.id).zfill(4)} - {self.amount} {self.state}"


class Validation(BaseModel):

    old_state = models.CharField(choices=STATE_PAYMENT, max_length=40)
    new_state = models.CharField(choices=STATE_PAYMENT, max_length=40)
    date = models.DateTimeField(auto_now_add=True) 
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    refusal_reason = models.TextField(blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)

    def __str__(self):
        return "Validation - " + str(str(self.payment.id).zfill(4)) + " - " + str(self.date)