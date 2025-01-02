from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Payment
from account.models import Zone
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

def send_recap_email(payments, subject, start_date, end_date, zone=None):
    validated_payments = payments.filter(state='Validé')
    confirmed_payments = payments.filter(state='Confirmé')
    refused_payments = payments.filter(state='Refusé')
    draft_payments = payments.filter(state='Brouillon')

    nbr_total = payments.count()
    validated_total = validated_payments.count()
    confirmed_total = confirmed_payments.count()
    refused_total = refused_payments.count()
    draft_total = draft_payments.count()

    amount_total = payments.aggregate(total=Sum('amount'))['total'] or 0
    amount_validated = validated_payments.aggregate(total=Sum('amount'))['total'] or 0
    amount_confirmed = confirmed_payments.aggregate(total=Sum('amount'))['total'] or 0
    amount_refused = refused_payments.aggregate(total=Sum('amount'))['total'] or 0
    amount_draft = draft_payments.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'validated_payments': validated_payments,
        'confirmed_payments': confirmed_payments,
        'refused_payments': refused_payments,
        'draft_payments': draft_payments,
        'nbr_total': nbr_total,
        'validated_total': validated_total,
        'confirmed_total': confirmed_total,
        'refused_total': refused_total,
        'draft_total': draft_total,
        'amount_total': amount_total,
        'amount_validated': amount_validated,
        'amount_confirmed': amount_confirmed,
        'amount_refused': amount_refused,
        'amount_draft': amount_draft,
        'zone': zone, 
        'payments': payments, 
        'from': start_date, 
        'to': end_date
    }

    addresses = []

    html_message = render_to_string('fragment/recap_email.html', context)
    if zone:
        addresses = zone.address.split('&') if zone.address else  ['mohammed.senoussaoui@grupopuma-dz.com']

    else:    
        addresses = [
        address for zone in Zone.objects.all() if zone.address
        for address in zone.address.split('&')
    ] or ['mohammed.senoussaoui@grupopuma-dz.com']
        
    addresses = list(set(addresses))
    
    email = EmailMultiAlternatives(subject, None, 'Puma Paiement', addresses)
    email.attach_alternative(html_message, "text/html")
    email.send()

def send_weekly_recap_email():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    payments = Payment.objects.filter(date__range=[start_date, end_date]).order_by('date_depot')

    for zone in Zone.objects.all():
        subject = f'Récapitulatif Hebdomadaire des Paiements - {zone.designation}'
        zone_payments = payments.filter(zone=zone)
        if zone_payments.exists():
            send_recap_email(zone_payments, subject, start_date, end_date, zone)
    
    subject = f'Récapitulatif Hebdomadaire des Paiements - GLOBAL'
    if payments.exists():
        send_recap_email(payments, subject, start_date, end_date)

def send_monthly_recap_email():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    payments = Payment.objects.filter(date__range=[start_date, end_date]).order_by('date_depot')

    for zone in Zone.objects.all():
        subject = f'Récapitulatif Mensuel des Paiements - {zone.designation}'
        zone_payments = payments.filter(zone=zone)
        if zone_payments.exists():
            send_recap_email(zone_payments, subject, start_date, end_date, zone)
    
    subject = f'Récapitulatif Mensuel des Paiements - GLOBAL'
    if payments.exists():
        send_recap_email(payments, subject, start_date, end_date)
