import datetime

from django import forms
from .models import Presupuesto, Categoria, Cuenta


DIRECCIONES_OPCIONES = (
    ("D", "Débito"),
    ("C", "Crédito")
)

DURACIONES_OPCIONES = (
    ("F", "Hasta fin de año"),
    ("M", "Sólo un mes")
)


class TransferenciaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class TransferenciaForm(forms.Form):
    fecha = forms.DateField(widget=forms.TextInput)
    de_cuenta = TransferenciaChoiceField(
        queryset=Cuenta.objects.all()
    )
    a_cuenta = TransferenciaChoiceField(
        queryset=Cuenta.objects.all()
    )
    monto = forms.IntegerField(localize=True)

    def __init__(self, *args, **kwargs):
        super(TransferenciaForm, self).__init__(*args, **kwargs)
        self.fields.get('fecha').widget.attrs = {
            "class": "form-control datepicker",
            "data-start-week-day": "0"
        }
        self.fields.get('de_cuenta').widget.attrs = {
            "class": "custom-select"
        }
        self.fields.get('de_cuenta').empty_label = "Elige una Cuenta..."
        self.fields.get('a_cuenta').widget.attrs = {
            "class": "custom-select"
        }
        self.fields.get('a_cuenta').empty_label = "Elige una Cuenta..."
        self.fields.get('monto').widget.attrs = {
            "class": "form-control"
        }


class AgregarPresupuestoForm(forms.Form):
    presupuesto = forms.CharField(widget=forms.TextInput)
    monto = forms.IntegerField(localize=True)
    mes_inicio = forms.DateField(widget=forms.TextInput)
    duracion = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DURACIONES_OPCIONES
    )

    def __init__(self, *args, **kwargs):
        super(AgregarPresupuestoForm, self).__init__(*args, **kwargs)
        self.fields.get('presupuesto').widget.attrs = {
            "class": "form-control"
        }
        self.fields.get('monto').widget.attrs = {
            "class": "form-control"
        }
        self.fields.get('mes_inicio').widget.attrs = {
            "class": "form-control datepicker",
            "data-start-week-day": "0"
        }
        self.fields.get('duracion').widget.attrs = {
            "class": "form-check-input"
        }


class MesForm(forms.Form):
    mes = forms.DateField(widget=forms.TextInput(attrs={
        "class": "form-control datepicker",
        "data-start-week-day": "0"
    }))


class AgregarTransaccionForm(forms.Form):
    beneficiario = forms.CharField()
    categoria = forms.CharField()
    direccion = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DIRECCIONES_OPCIONES,
        initial="D"
    )
    fecha = forms.DateField(widget=forms.TextInput)
    monto = forms.IntegerField(localize=True)
    presupuesto = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(AgregarTransaccionForm, self).__init__(*args, **kwargs)
        self.fields.get('beneficiario').widget.attrs = {
            "class": "form-control"
        }
        self.fields['categoria'] = forms.ModelChoiceField(
            queryset=Categoria.objects.all(),
            required=False
        )
        self.fields.get('categoria').widget.attrs = {
            "class": "custom-select"
        }
        self.fields.get('direccion').widget.attrs = {
            "class": "form-check-input"
        }
        self.fields.get('fecha').widget.attrs = {
            "class": "form-control datepicker",
            "data-start-week-day": "0"
        }
        self.fields.get('monto').widget.attrs = {
            "class": "form-control"
        }
        self.fields['presupuesto'] = forms.ModelChoiceField(
            queryset=Presupuesto.objects.all(),
            required=False
        )
        self.fields.get('presupuesto').widget.attrs = {
            "class": "custom-select"
        }


class FechaRangoForm(forms.Form):
    treinta_dias_atras = datetime.datetime.today() + datetime.timedelta(-30)
    treinta_dias_atras = treinta_dias_atras.strftime("%d-%m-%Y")
    fecha_inicio = forms.DateField(widget=forms.TextInput(attrs={
        "class": "form-control datepicker",
        "data-start-date": treinta_dias_atras,
        "data-start-week-day": "0"
    }))
    fecha_fin = forms.DateField(widget=forms.TextInput(attrs={
        "class": "form-control datepicker",
        "data-start-week-day": "0"
    }))
