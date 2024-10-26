from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Payment
from account.models import Zone
from django.utils import timezone
from datetime import timedelta

def send_zone_recap_email(zone, payments, subject, start_date, end_date):
    html_message = render_to_string('fragment/recap_email.html', {'zone': zone, 'payments': payments, 'from': start_date, 'to': end_date})
    addresses = zone.address.split('&') if zone.address else  ['mohammed.senoussaoui@grupopuma-dz.com']
    
    email = EmailMultiAlternatives(subject, None, 'Puma Paiement', addresses)
    email.attach_alternative(html_message, "text/html")
    email.send()

def send_weekly_recap_email():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    subject = f'Recapitulatif Hebdomadaire des Paiements - Semaine se terminant le {end_date.strftime("%d/%m/%Y")}'
    
    for zone in Zone.objects.all():
        payments = Payment.objects.filter(zone=zone, date__range=[start_date, end_date], state='Validé')
        if payments.exists():
            send_zone_recap_email(zone, payments, subject, start_date, end_date)

def send_monthly_recap_email():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    subject = f'Recapitulatif Mensuel des Paiements - Mois se terminant le {end_date.strftime("%d/%m/%Y")}'
    
    for zone in Zone.objects.all():
        payments = Payment.objects.filter(zone=zone, date__range=[start_date, end_date], state='Validé')
        if payments.exists():
            send_zone_recap_email(zone, payments, subject, start_date, end_date)
