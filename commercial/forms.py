from account.forms import BaseModelForm, getAttrs
from django.utils import timezone
from django.db.models import Q
from django import forms
from .models import *
from django.forms import ClearableFileInput

class BankForm(BaseModelForm):
    class Meta:
        model = Bank
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Nom de la banque')))

class PaymentTypeForm(BaseModelForm):
    class Meta:
        model = PaymentType
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Type de Paiment')))

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'fragments/custom_clearable_file_input.html'

class PaymentForm(BaseModelForm):
    class Meta:
        model = Payment
        fields = ['commercial', 'client_id', 'client', 'zone', 'bank', 'payment_type', 'ref', 'date', 'amount', 'check_image', 'observation']

    commercial = forms.ModelChoiceField(queryset=User.objects.filter(Q(role='Commercial') | Q(role='Admin')), widget=forms.Select(attrs=getAttrs('select')), empty_label="Commercial")
    
    client_id = forms.IntegerField(widget=forms.HiddenInput(attrs=getAttrs('controlID','ID_client_id')))
    client = forms.CharField(widget=forms.TextInput(attrs=getAttrs('controlSearch','Client')))
    
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Zone")
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Banque")
    payment_type = forms.ModelChoiceField(queryset=PaymentType.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Type de Paiment")
    ref = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Référence')), required=False)
    date = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs=getAttrs('control', 'Montant', {'min': 0.01})))
    # check_image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}), required=False)
    check_image = forms.ImageField(widget=CustomClearableFileInput(attrs={'class': 'd-none', 'id': 'check-image-input', 'accept': 'image/*'}), required=False)
    observation = forms.CharField(widget=forms.Textarea(attrs= getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        if user is not None:
            zones = user.zones.all()
            self.fields['commercial'].initial = user
            self.fields['zone'].queryset = zones
            self.fields['zone'].initial = zones.first()
            if not user.role == 'Admin': 
                self.fields['commercial'].widget.attrs['disabled'] = True
            if len(zones) < 2:
                self.fields['zone'].widget.attrs['disabled'] = True
