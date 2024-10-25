from django_filters import ChoiceFilter, CharFilter, ModelChoiceFilter, FilterSet, DateFilter
from django import forms
from .forms import getAttrs
from .models import *
from django.db.models import Q

class BankFilter(FilterSet):
    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Banque..') ))
    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(designation__icontains=value)).distinct()
    class Meta:
        model = Bank
        fields = ['search']

class PaymentTypeFilter(FilterSet):
    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Type de Paiment..')))
    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(designation__icontains=value)).distinct()
    class Meta:
        model = PaymentType
        fields = ['search']

class PaymentFilter(FilterSet):

    other = {'style': 'background-color: rgba(202, 207, 215, 0.5); box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #45558a; height: 40px; border-radius: 5px;'}
    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))
    state = ChoiceFilter(choices=STATE_PAYMENT, widget=forms.Select(attrs=getAttrs('select')), empty_label="État")
    start_date = DateFilter(field_name='date', lookup_expr='gte', widget=forms.widgets.DateInput(format=('%Y-%m-%d'), attrs=getAttrs('date')))
    end_date = DateFilter(field_name='date', lookup_expr='lte', widget=forms.widgets.DateInput(format=('%Y-%m-%d'), attrs=getAttrs('date')))
    zone = ModelChoiceFilter(queryset=Zone.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Zone")
    payment_type = ModelChoiceFilter(queryset=PaymentType.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Type de Paiement")

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(ref__icontains=value) | Q(commercial__fullname__icontains=value) | Q(zone__designation__icontains=value) | Q(bank__designation__icontains=value) | Q(payment_type__designation__icontains=value)).distinct()

    class Meta:
        model = Payment
        fields = ['search', 'state', 'start_date', 'end_date', 'zone', 'payment_type']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PaymentFilter, self).__init__(*args, **kwargs)
        if user:
            self.filters['zone'].queryset = user.zones.all()

