from django.urls import path

from . import views

app_name = 'finanzas'

urlpatterns = [
    # cuentas
    path(
        'cuentas/',
        views.ResumenCuentas.as_view(),
        name='cuentas'
    ),
    # presupuestos
    path(
        'presupuestos/',
        views.ResumenPresupuestos.as_view(),
        name='presupuestos'
    ),
    # transacciones
    path(
        'transacciones/<slug:cuenta>/',
        views.ResumenTransacciones.as_view(),
        name='transacciones'
    )
]
