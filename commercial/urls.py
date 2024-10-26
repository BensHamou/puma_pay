from django.urls import path
from .views import *


urlpatterns = [
    
    path('bank/all/', listBankView, name='banks'),
    path('bank/create/', createBankView, name='create_bank'),
    path('bank/edit/<int:id>/', editBankView, name='edit_bank'),
    path('bank/delete/<int:id>/', deleteBankView, name='delete_bank'),

    path('payment-type/all/', listPaymentTypeView, name='payment_types'),
    path('payment-type/create/', createPaymentTypeView, name='create_payment_type'),
    path('payment-type/edit/<int:id>/', editPaymentTypeView, name='edit_payment_type'),
    path('payment-type/delete/<int:id>/', deletePaymentTypeView, name='delete_payment_type'),

    path('payment/all/', listPaymentView, name='payments'),
    path('', listPaymentView, name='payments'),
    path('payment/create/', createPaymentView, name='create_payment'),
    path('payment/edit/<int:id>/', editPaymentView, name='edit_payment'),
    path('payment/delete/<int:id>/', deletePaymentView, name='delete_payment'),
    path('payment/<int:pk>/detail/', detail_payment, name='detail_payment'),
    
    path('live_search/', live_search, name='live_search'),
    
    path('payment/<int:pk>/confirm/', confirmPayment, name='confirm_payment'),
    path('payment/<int:pk>/cancel/', cancelReport, name='cancel_payment'),
    path('payment/<int:pk>/validate/', validateReport, name='validate_payment'),
    path('payment/<int:pk>/refuse/', refuseReport, name='refuse_payment'),

]

