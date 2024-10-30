from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from datetime import timedelta
from django import forms
from .models import *
from django import forms
from django.utils import timezone

today = timezone.now().date()
start_of_week = today - timedelta(days=today.weekday() + 1)
end_of_week = start_of_week + timedelta(days=6)

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
        fields = ['zone', 'date_from', 'date_to', 'amount']

    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Zone")
    date_from = forms.DateField(initial=start_of_week, widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    date_to = forms.DateField(initial=end_of_week, widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    amount = forms.DecimalField(max_digits=14, decimal_places=2, widget=forms.NumberInput(attrs=getAttrs('control', 'Montant de l\'objectif', {'min': 0.01})))

    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get("zone")
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to:
            if (date_to - date_from).days != 6:
                self.add_error('date_to', "La période doit être exactement de 7 jours.")
                raise ValidationError("La période entre date_from et date_to doit être de 7 jours.")

            if date_from.weekday() != 6:
                self.add_error('date_from', "La date de début doit être un dimanche.")
            if date_to.weekday() != 5:
                self.add_error('date_to', "La date de fin doit être un samedi.")
            
            if self.errors:
                raise ValidationError("Veuillez vérifier que la période commence un dimanche, se termine un samedi et dure 7 jours.")
        
        if zone and date_from and date_to:
            overlapping_objectives = Objective.objects.filter(zone=zone,date_from__lte=date_to,date_to__gte=date_from).exclude(id=self.instance.pk)
            if overlapping_objectives.exists():
                self.add_error('zone', f"Un objectif existe déjà pour cette zone au period {date_from} - {date_to}.")
                self.add_error('date_from', f"Un objectif existe déjà pour la zone {zone} durant cette période.")
                self.add_error('date_to', f"Un objectif existe déjà pour la zone {zone} durant cette période.")
                raise ValidationError(f"Un objectif existe déjà pour la zone {zone} entre {date_from} et {date_to}.")
        return cleaned_data