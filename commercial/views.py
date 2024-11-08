from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages 
from django.db.models import Sum
from account.decorators import *
from django.urls import reverse
from datetime import timedelta 
from .utils import getClientId, getPayerId
from functools import wraps
from .filters import *
from .models import *
from .forms import *

def check_creator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.has_admin():
            return view_func(request, *args, **kwargs)
        paytment_id = kwargs.get('pk')
        payment = Payment.objects.get(id=paytment_id)
        if request.user.has_commercial() and payment.commercial == request.user and payment.state == 'Brouillon':
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper

def check_validator(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.has_admin():
            return view_func(request, *args, **kwargs)
        paytment_id = kwargs.get('pk')
        payment = Payment.objects.get(id=paytment_id)
        if request.user.has_backoffice() and payment.zone in request.user.zones.all() and payment.state == 'Confirmé':
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper

def can_view_payment(view_func):
    def wrapper(request, *args, **kwargs):
        paytment_id = kwargs.get('pk')
        payment = Payment.objects.get(id=paytment_id)
        if request.user.has_admin():
            return view_func(request, *args, **kwargs)
        if request.user.has_backoffice() and payment.zone in request.user.zones.all():
            return view_func(request, *args, **kwargs)
        if request.user.has_commercial() and (payment.commercial == request.user or request.user.role == 'Zone Manageur'):
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper

def can_create(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.has_admin() or request.user.has_commercial():
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper

def can_edit(view_func):
    def wrapper(request, *args, **kwargs):
        paytment_id = kwargs.get('pk')
        if not paytment_id:
            paytment_id = kwargs.get('id')
        payment = Payment.objects.get(id=paytment_id)
        if request.user.has_admin():
            return view_func(request, *args, **kwargs)
        if request.user.has_commercial() and payment.commercial == request.user:
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper

# BANKS

@login_required(login_url='login')
@admin_required
def listBankView(request):
    banks = Bank.objects.all().order_by('-date_modified')
    filteredData = BankFilter(request.GET, queryset=banks)
    banks = filteredData.qs
    paginator = Paginator(banks, request.GET.get('page_size', 12))
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filteredData': filteredData}
    return render(request, 'list_banks.html', context)

@login_required(login_url='login')
@admin_required
def deleteBankView(request, id):
    bank = get_object_or_404(Bank, id=id)
    try:
        bank.delete()
        url_path = reverse('banks')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de la banque: {e}")
        return redirect(getRedirectionURL(request, reverse('banks')))

@login_required(login_url='login')
@admin_required
def createBankView(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save(user=request.user) 
            url_path = reverse('banks')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form}
    return render(request, 'bank_form.html', context)

@login_required(login_url='login')
@admin_required
def editBankView(request, id):
    bank = get_object_or_404(Bank, id=id)
    form = BankForm(instance=bank)
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('banks')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form, 'bank': bank}
    return render(request, 'bank_form.html', context)

# PAYMENT TYPES

@login_required(login_url='login')
@admin_required
def listPaymentTypeView(request):
    payment_types = PaymentType.objects.all().order_by('-date_modified') 
    filteredData = PaymentTypeFilter(request.GET, queryset=payment_types)
    payment_types = filteredData.qs
    paginator = Paginator(payment_types, request.GET.get('page_size', 12))
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filteredData': filteredData}
    return render(request, 'list_payment_types.html', context)

@login_required(login_url='login')
@admin_required
def deletePaymentTypeView(request, id):
    payment_type = get_object_or_404(PaymentType, id=id)
    try:
        payment_type.delete()
        url_path = reverse('payment_types')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression du type de paiement: {e}")
        return redirect(getRedirectionURL(request, reverse('payment_types')))

@login_required(login_url='login')
@admin_required
def createPaymentTypeView(request):
    form = PaymentTypeForm()
    if request.method == 'POST':
        form = PaymentTypeForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('payment_types')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form}
    return render(request, 'payment_type_form.html', context)

@login_required(login_url='login')
@admin_required
def editPaymentTypeView(request, id):
    payment_type = get_object_or_404(PaymentType, id=id)
    form = PaymentTypeForm(instance=payment_type)
    if request.method == 'POST':
        form = PaymentTypeForm(request.POST, instance=payment_type)
        if form.is_valid():
            form.save(user=request.user)
            url_path = reverse('payment_types')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form, 'payment_type': payment_type}
    return render(request, 'payment_type_form.html', context)

# PAYMENTS

@login_required(login_url='login')
def listPaymentView(request):

    if request.user.has_admin():
        payments = Payment.objects.all().order_by('-date_modified')
    elif request.user.role == 'Zone Manageur':
        payments = Payment.objects.filter(zone__in=request.user.zones.all()).order_by('-date_modified')
    elif request.user.has_commercial():
        payments = Payment.objects.filter(commercial=request.user).order_by('-date_modified')
    else:
        payments = Payment.objects.filter(zone__in=request.user.zones.all()).order_by('-date_modified')

    time_filter = request.GET.get('time_filter')
    if time_filter == 'today':
        payments = payments.filter(date=timezone.now().date()) 
    elif time_filter == 'week':
        start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
        payments = payments.filter(date__gte=start_of_week)
    elif time_filter == 'month':
        payments = payments.filter(date__month=timezone.now().month)

    filteredData = PaymentFilter(request.GET, queryset=payments, user=request.user)
    total_lines = filteredData.qs.count()
    payments = filteredData.qs
    paginator = Paginator(payments, request.GET.get('page_size', 12))

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    fetched_lines = len(page.object_list)

    widgets = getWidgets(request)

    context = {'page': page, 'filteredData': filteredData, 'fetched_lines': fetched_lines, 'total_lines': total_lines, 'widgets': widgets}
    return render(request, 'list_payments.html', context)

@login_required(login_url='login')
@admin_required
def deletePaymentView(request, id):
    payment = get_object_or_404(Payment, id=id)
    try:
        payment.delete()
        url_path = reverse('payments')
        return redirect(getRedirectionURL(request, url_path))
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression du paiement: {e}")
        return redirect(getRedirectionURL(request, reverse('payments')))

@login_required(login_url='login')
@can_create
def createPaymentView(request):
    form = PaymentForm(user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            payment = form.save(user=request.user, commit=False)
            payment.state = 'Brouillon'
            payment.save()
            url_path = reverse('payments')
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form}
    return render(request, 'payment_form.html', context)

@login_required(login_url='login')
@can_edit
def editPaymentView(request, id):
    payment = get_object_or_404(Payment, id=id)
    original_check_image = payment.check_image 
    original_deposit_image = payment.deposit_image 
    form = PaymentForm(instance=payment, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES, instance=payment, user=request.user)
        if form.is_valid():
            payment = form.save(user=request.user, commit=False)
            if not payment.check_image and original_check_image:
                original_check_image.delete(save=False)
            if not payment.deposit_image and original_deposit_image:
                original_deposit_image.delete(save=False)
            payment.save()
            url_path = reverse('detail_payment', args=[payment.id])
            return redirect(getRedirectionURL(request, url_path))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    context = {'form': form, 'payment': payment}
    return render(request, 'payment_form.html', context)

@login_required(login_url='login')
@can_view_payment
def detail_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)    
    
    is_admin = request.user.role == 'Admin'
    is_commercial = request.user.role in ['Commercial', 'Zone Manageur']
    is_back_office = request.user.role == 'Back Office'
    is_draft = payment.state == 'Brouillon'
    is_confirmed = payment.state == 'Confirmé'
    
    context = {
        'payment': payment,
        'is_admin': is_admin,
        'is_commercial': is_commercial,
        'is_back_office': is_back_office,
        'is_draft': is_draft,
        'is_confirmed': is_confirmed,
    }

    return render(request, 'detail_payment.html', context)

@login_required(login_url='login')
def live_search(request):
    search_for = request.GET.get('search_for', '')
    term = request.GET.get('search_term', '')

    if search_for == 'payer':
        records = getPayerId(term)
    elif search_for == 'client':
        records = getClientId(term)

    if len(records) > 0:
        return JsonResponse([{'id': obj[0], 'name': f'''{obj[1]}'''.replace("'","\\'")} for obj in records], safe=False)
        
    return JsonResponse([], safe=False)

@login_required(login_url='login')
@check_creator
def confirmPayment(request, pk):
    if request.method == 'POST':
        payment, success, validation = changeState(request, pk, 'Confirmé')
        if success:
            send_email(payment)
            return JsonResponse({'success': True, 'message': 'Paiement confirmé avec succès.', 'payment_id': payment.id})
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement n\'existe pas.'})
    return JsonResponse({'success': False, 'message': 'Méthode de demande non valide.'})

@login_required(login_url='login')
@check_creator
def cancelReport(request, pk):
    if request.method == 'POST':
        payment, success, validation = changeState(request, pk, 'Annulé')
        if success:
            return JsonResponse({'success': True, 'message': 'Paiement anulé avec succès.', 'payment_id': payment.id})
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement n\'existe pas.'})
    return JsonResponse({'success': False, 'message': 'Méthode de demande non valide.'})

@login_required(login_url='login')
@check_validator
def validateReport(request, pk):
    if request.method == 'POST':
        payment, success, validation = changeState(request, pk, 'Validé')
        if success:
            return JsonResponse({'success': True, 'message': 'Paiement validé avec succès.', 'payment_id': payment.id})
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement n\'existe pas.'})
    return JsonResponse({'success': False, 'message': 'Méthode de demande non valide.'})

@login_required(login_url='login')
@check_validator
def refuseReport(request, pk):
    if request.method == 'POST':
        payment, success, validation = changeState(request, pk, 'Refusé')
        if success:
            send_email(payment, validation)
            return JsonResponse({'success': True, 'message': 'Paiement refusé avec succès.', 'payment_id': payment.id})
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement n\'existe pas.'})
    return JsonResponse({'success': False, 'message': 'Méthode de demande non valide.'})

def createValidation(request, payment, new_state, refusal_reason=None):
    old_state = payment.state
    payment.state = new_state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason=refusal_reason, payment=payment)
    payment.save()
    validation.save()
    messages.success(request, f'Payment set to {new_state} successfully')
    return validation

def changeState(request, pk, action):
    try:
        payment = Payment.objects.get(id=pk)
    except Payment.DoesNotExist:
        messages.success(request, 'Le paiement n\'existe pas')
        return payment, False
    if payment.state == action:
        return payment, True
    validation = createValidation(request, payment, action, request.POST.get('refusal_reason', None))
    return payment, True, validation

def send_email(payment, validation=False):
    subject = f'Paiement ID[{str(payment.id).zfill(4)}]'
    if validation:
        subject += ' - Refusé'
        html_message = render_to_string('fragment/payment_refusal.html', {'payment': payment, 'validation': validation})
    else:
        html_message = render_to_string('fragment/payment_confirmation.html', {'payment': payment})

    addresses = payment.zone.address.split('&')
    if not addresses:
        addresses = ['mohammed.senoussaoui@grupopuma-dz.com']
    
    email = EmailMultiAlternatives(subject, None, 'Puma Paiement', addresses)
    email.attach_alternative(html_message, "text/html") 
    if payment.check_image:
        email.attach(payment.check_image.name, payment.check_image.read(), 'image/jpeg')
    if payment.deposit_image:
        email.attach(payment.deposit_image.name, payment.deposit_image.read(), 'image/jpeg')

    email.send()

def get_zone_widget(zone, current_month, current_year):
    payments = Payment.objects.filter(zone=zone, state='Validé')

    try:
        monthly_objective = Objective.objects.get(zone=zone, month__month=current_month, month__year=current_year)
        monthly_objective_value = monthly_objective.amount 
    except Objective.DoesNotExist:
        monthly_objective_value = 0

    weekly_objective_value = round(monthly_objective_value / 4)

    start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
    weekly_payments = payments.filter(date_depot__gte=start_of_week)
    weekly_payment_sum = weekly_payments.aggregate(sum=Sum('amount'))['sum'] or 0
    total_weekly_payments = weekly_payments.count()

    monthly_payments = payments.filter(date_depot__month=current_month, date_depot__year=current_year)
    monthly_payment_sum = monthly_payments.aggregate(sum=Sum('amount'))['sum'] or 0
    total_monthly_payments = monthly_payments.count()

    weekly_widget = {
        'title': f'Récap Hebdomadaire - {zone.designation}',
        'elements': [
            {'label': 'Objectif', 'value': format_amount(weekly_objective_value)}, 
            {'label': 'Somme des paiements', 'value': format_amount(weekly_payment_sum), 'color': getColor(weekly_objective_value, weekly_payment_sum)},
            {'label': 'Total des paiements', 'value': f"{total_weekly_payments} paiements"},
        ],
        'image': 'img/hebdomadaire.png',
        'active': False
    }

    monthly_widget = {
        'title': f'Récap Mensuelle - {zone.designation}',
        'elements': [
            {'label': 'Objectif mensuelle', 'value': format_amount(monthly_objective_value)},
            {'label': 'Somme des paiements', 'value': format_amount(monthly_payment_sum), 'color': getColor(monthly_objective_value, monthly_payment_sum)},
            {'label': 'Total des paiements', 'value': f"{total_monthly_payments} paiements"},
        ],
        'image': 'img/mensuelle.png',
        'active': False
    }

    return [weekly_widget, monthly_widget]

def getWidgets(request):
    user_zones = request.user.zones.all()
    current_month = timezone.now().month
    current_year = timezone.now().year

    widgets = []
    for zone in user_zones:
        widgets.extend(get_zone_widget(zone, current_month, current_year))

    widgets[0]['active'] = True

    return widgets

def getColor(A, B):
    C = A  - B
    if B >= A:
        return "green"
    elif C >= 50000: 
        return "red"
    elif C > 0: 
        return "orange"
    else:
        return "blue" 

def format_amount(amount):
    if amount >= 1_000_000:  # Check for millions first
        return f"{amount / 1_000_000:,.1f}M DZD"
    elif amount >= 1000:
        return f"{amount / 1000:,.1f}K DZD"
    else:
        return f"{amount:,.2f} DZD"