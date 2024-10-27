from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from datetime import datetime
from django import forms
from .models import *

def getAttrs(type, placeholder='', other={}):
    ATTRIBUTES = {
        'control': {'class': 'form-control', 'style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;', 'placeholder': ''},
        'login': {'class': 'form-control', 'style': 'padding-left: 30px; background-color: white; height: 45px; border: 1px solid #ccc; border-radius: 100px;', 'placeholder': ''},
        'controlID': {'class': 'form-control search-input-id', 'autocomplete': "off", 'style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;', 'placeholder': ''},
        'controlSearch': {'class': 'form-control search-input', 'autocomplete': "off", 'style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;', 'placeholder': ''},
        'search': {'class': 'form-control mb-lg-0 mb-3', 'style': 'padding-left: 30px; margin-right: 10px; border-radius: 100px; max-width: 500px', 'type': 'text', 'placeholder': '', 'id': 'search'},
        'select': {'class': 'form-select', 'style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;'},
        'select2': {'class': 'form-select select2', 'style': 'background-color: #ffffff; padding-left: 30px; width: 100%; border-radius: 100px;'},
        'select3': {'class': 'form-select select3', 'style': 'background-color: #ffffff; padding-left: 30px; width: 100%; border-radius: 100px;'},
        'date': {'type': 'date', 'class': 'form-control dateinput','style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;'},
        'month': {'type': 'month', 'class': 'form-control dateinput','style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;'},
        'time': {'type': 'time', 'class': 'form-control timeinput', 'style': 'background-color: #ffffff; padding-left: 30px; border-radius: 100px;', 'placeholder': ''},
        'textarea': {"rows": "3", 'style': 'width: 100%', 'class': 'form-control', 'placeholder': '', 'style': 'padding-left: 30px; background-color: #ffffff; border-radius: 50px;'}
    }

    if type in ATTRIBUTES:
        attributes = ATTRIBUTES[type]
        if 'placeholder' in attributes:
            attributes['placeholder'] = placeholder
        if other:
            attributes.update(other)
        return attributes
    else:
        return {}
    
class BaseModelForm(ModelForm):
    def save(self, commit=True, user=None):
        instance = super(BaseModelForm, self).save(commit=False)
        if user:
            if not instance.pk:
                instance.create_uid = user
            instance.write_uid = user
        if commit:
            instance.save()
        return instance
    
class UserForm(BaseModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_admin', 'first_name', 'last_name', 'role', 'zones']

    username = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Nom d\'utilisateur')), disabled=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Nom de famille')), disabled=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Prénom')), disabled=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs=getAttrs('control', 'Email')), disabled=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs=getAttrs('select')))
    zones = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.SelectMultiple(attrs=getAttrs('select3')), required=False)
    is_admin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'type': 'checkbox',
        'data-onstyle': 'primary',
        'data-toggle': 'switchbutton',
        'data-onlabel': "Admin", 
        'data-offlabel': "User"
    }))
    
class CustomLoginForm(AuthenticationForm):
    
    username = forms.CharField(label="Email / AD 2000", widget=forms.TextInput(attrs=getAttrs('login', 'Adresse e-mail', {'autofocus': True})))
    password = forms.CharField(widget=forms.PasswordInput(attrs=getAttrs('login', 'Mot de passe')))


class ZoneForm(BaseModelForm):
    class Meta:
        model = Zone
        fields = ['designation', 'address']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Nom de la zone')))
    address = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Address')))



class ObjectiveForm(BaseModelForm):
    class Meta:
        model = Objective
        fields = ['zone', 'month', 'amount']

    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Zone")
    month = forms.DateField(widget=forms.DateInput(attrs=getAttrs('month', 'Mois')), input_formats=['%Y-%m'], help_text="Format: YYYY-MM" )
    amount = forms.DecimalField(max_digits=14, decimal_places=2, widget=forms.NumberInput(attrs=getAttrs('control', 'Montant de l\'objectif', {'min': 0.01})))
    
    def clean_month(self):
        month = self.cleaned_data.get('month')
        if month is None:
            raise ValidationError("Le mois est requis.")
        return month

    def save(self, user=None, commit=True):
        objective = super().save(commit=False, user=user)
        if isinstance(self.cleaned_data['month'], str):
            objective.month = datetime.strptime(self.cleaned_data['month'], '%Y-%m').date()
        else:
            objective.month = self.cleaned_data['month']
        if commit:
            objective.save()
        return objective
    
    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get("zone")
        month = cleaned_data.get("month")
        if zone and month:
            if Objective.objects.filter(zone=zone, month=month).exists():
                self.add_error('zone', f"Un objectif existe déjà pour cette zone au mois de {month}.")
                self.add_error('month', f"Un objectif existe déjà pour la zone {zone} au ce mois.")
                raise ValidationError(f"Un objectif existe déjà pour la zone {zone} au mois de {month}.")
        return cleaned_data