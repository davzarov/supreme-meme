import datetime

from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import View

from .forms import (AgregarPresupuestoForm, AgregarTransaccionForm,
                    FechaRangoForm, MesForm, TransferenciaForm)
from .models import (Categoria, Cuenta, Presupuesto, PresupuestoMensual,
                     Transaccion)


class ResumenCuentas(View):
    def get_context_data(self, *args, **kwargs):
        transferencia_form = TransferenciaForm()
        filtro_form = FechaRangoForm()
        cuentas = Cuenta.objects.all().order_by('nombre')
        categorias = Categoria.objects.all()
        presupuestos = Presupuesto.objects.all()
        if 'fecha_inicio' and 'fecha_fin' in kwargs:
            fecha_inicio = kwargs['fecha_inicio']
            fecha_fin = kwargs['fecha_fin']
        else:
            fecha_inicio = datetime.datetime.today() + datetime.timedelta(-30)
            fecha_fin = datetime.datetime.today()

        cabecera_grafico = fecha_inicio \
            .strftime("%d %b %Y") + " - " + fecha_fin.strftime("%d %b %Y")
        presupuesto_data = {}
        categoria_data = {}

        for presupuesto in presupuestos:
            subcategoria = {}
            if Transaccion.objects.filter(
                    presupuesto__presupuesto=presupuesto.id,
                    debit=True,
                    fecha__range=[fecha_inicio, fecha_fin]).count():
                monto = Transaccion.objects.filter(
                    presupuesto__presupuesto=presupuesto.id,
                    debit=True,
                    fecha__range=[fecha_inicio, fecha_fin]).aggregate(Sum('monto'))
                presupuesto_data[presupuesto.nombre] = monto['monto__sum']
                for categoria in categorias:
                    if Transaccion.objects.filter(
                            presupuesto__presupuesto=presupuesto.id,
                            categoria=categoria.id,
                            debito=True,
                            fecha__range=[fecha_inicio, fecha_fin]).count():
                        monto_categoria = Transaccion.objects.filter(
                            presupuesto__presupuesto=presupuesto.id,
                            categoria=categoria.id,
                            debito=True,
                            fecha__range=[fecha_inicio, fecha_fin]).aggregate(Sum('monto'))
                        subcategoria[categoria.nombre] = monto_categoria['monto__sum']
                    if Transaccion.objects.filter(
                            presupuesto__presupuesto=presupuesto.id,
                            categoria__isnull=True,
                            debito=True,
                            fecha__range=[fecha_inicio, fecha_fin]).count():
                        monto_categoria = Transaccion.objects.filter(
                            presupuesto__presupuesto=presupuesto.id,
                            categoria__isnull=True).aggregate(Sum('monto'))
                        subcategoria['Sin Categorizar'] = monto_categoria['monto__sum']
                categoria_data[presupuesto.nombre] = subcategoria
        context = {
            'cuentas': cuentas,
            'transferencia_form': transferencia_form,
            'cabecera_grafico': cabecera_grafico,
            'presupuesto_data': presupuesto_data,
            'categoria_data': categoria_data,
            'filtro_form': filtro_form
        }
        return context

    def get(self, request):
        return render(request, 'finanzas/resumen_cuentas.html', self.get_context_data(request))

    def post(self, request):
        transferencia_form = TransferenciaForm(request.POST)
        accion = request.POST['accion']
        if accion == 'transferencia':
            if transferencia_form.is_valid():
                transferencia_data = {}
                for k, v in transferencia_form.cleaned_data.items():
                    transferencia_data[k] = v
                nuevo_balance_de_cuenta = transferencia_data['de_cuenta'] - \
                    transferencia_data['monto']
                transferencia_data['de_cuenta'].balance = nuevo_balance_de_cuenta
                transferencia_data['de_cuenta'].save()
                nuevo_balance_a_cuenta = transferencia_data['a_cuenta'] + \
                    transferencia_data['monto']
                transferencia_data['a_cuenta'].balance = nuevo_balance_a_cuenta
                transferencia_data['a_cuenta'].save()
                # credito
                Transaccion.objects.create(
                    balance=nuevo_balance_a_cuenta,
                    beneficiario=f"TRANSFERENCIA DESDE {transferencia_data['de_cuenta']}",
                    cuenta=transferencia_data['a_cuenta'],
                    debito=False,
                    fecha=transferencia_data['fecha'],
                    monto=transferencia_data['monto'],
                    transferencia=True
                )
                # debito
                Transaccion.objects.create(
                    balance=nuevo_balance_de_cuenta,
                    beneficiario=f"TRANSFERENCIA A {transferencia_data['a_cuenta']}",
                    cuenta=transferencia_data['de_cuenta'],
                    debito=True,
                    fecha=transferencia_data['fecha'],
                    monto=transferencia_data['monto'],
                    transferencia=True
                )
                fecha_inicio = datetime.datetime.today() + datetime.timedelta(-30)
                fecha_fin = datetime.datetime.today()
        elif accion == 'filtro_fecha':
            filtro_form = FechaRangoForm(request.POST)
            if filtro_form.is_valid():
                fecha_inicio = filtro_form.cleaned_data['fecha_inicio']
                fecha_fin = filtro_form.cleaned_data['fecha_fin']
        return render(request, 'finanzas/resumen_cuentas', self.get_context_data(
            request,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        ))


class ResumenPresupuestos(View):
    def get(self, request):
        presupuesto_form = AgregarPresupuestoForm()
        filtro_form = MesForm()
        ahora = datetime.datetime.now()
        presupuestos_mensuales = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        )
        encabezado = ahora.strftime("%B") + " " + str(ahora.year)
        total_planificado = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        ).aggregate(Sum('planificado'))
        total_actual = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        ).aggregate(Sum('actual'))
        efectivo_entrante = Transaccion.objects.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month,
            debito=False,
            transferencia=False
        ).aggregate(Sum('monto'))
        efectivo_saliente = Transaccion.objects.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month,
            debito=True,
            transferencia=False
        ).aggregate(Sum('monto'))
        context = {
            'efectivo_saliente': efectivo_saliente,
            'efectivo_entrante': efectivo_entrante,
            'presupuestos_mensuales': presupuestos_mensuales,
            'presupuesto_form': presupuesto_form,
            'encabezado': encabezado,
            'filtro_form': filtro_form,
            'total_planificado': total_planificado,
            'total_actual': total_actual
        }
        return render(request, 'finanzas/presupuesto_mensual.html', context)

    def post(self, request):
        presupuesto_form = AgregarPresupuestoForm()
        filtro_form = MesForm()
        ahora = datetime.datetime.now()
        accion = request.POST['accion']
        presupuestos_mensuales = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        )
        encabezado = ahora.strftime("%B") + " " + str(ahora.year)
        total_planificado = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        ).aggregate(Sum('planificado'))
        total_actual = PresupuestoMensual.objects.filter(
            mes__year=ahora.year,
            mes__month=ahora.month
        ).aggregate(Sum('actual'))
        efectivo_entrante = Transaccion.objects.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month,
            debito=False,
            transferencia=False
        ).aggregate(Sum('monto'))
        efectivo_saliente = Transaccion.objects.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month,
            debito=True,
            transferencia=False
        ).aggregate(Sum('monto'))
        if accion == 'agregar_presupuesto':
            presupuesto_form = AgregarPresupuestoForm(request.POST)
            if presupuesto_form.is_valid():
                presupuesto_data = {}
                for k, v in presupuesto_form.cleaned_data.items():
                    presupuesto_data[k] = v
                nuevo_presupuesto = Presupuesto.objects.filter(
                    nombre=presupuesto_data['presupuesto']).first()
                if nuevo_presupuesto:
                    pass
                else:
                    nuevo_presupuesto = Presupuesto.objects.create(
                        nombre=presupuesto_data['presupuesto']
                    )
                if presupuesto_data['duracion'] == 'M':
                    PresupuestoMensual.objects.create(
                        presupuesto=nuevo_presupuesto,
                        mes=presupuesto_data['mes_inicio'],
                        planificado=presupuesto_data['monto'],
                        actual=0
                    )
                else:
                    inicio = presupuesto_data['mes_inicio']
                    mes_inicio = int(inicio.month)
                    anio_inicio = int(inicio.year)
                    meses = []
                    while mes_inicio < 13:
                        meses.append(mes_inicio)
                        mes_inicio += 1
                    print(meses)
                    for mes in meses:
                        presupuesto_mes = str(
                            datetime.date(anio_inicio, mes, 1))
                        PresupuestoMensual.objects.create(
                            presupuesto=nuevo_presupuesto,
                            mes=presupuesto_mes,
                            planificado=presupuesto_data['monto'],
                            actual=0
                        )
                total_planificado = PresupuestoMensual.objects.filter(
                    mes__year=ahora.year,
                    mes__month=ahora.month
                ).aggregate(Sum('planificado'))
        elif accion == 'filtro_fecha':
            filtro_form = MesForm(request.POST)
            if filtro_form.is_valid():
                mes = filtro_form.cleaned_data['mes']
                encabezado = mes.strftime("%B") + " " + str(mes.year)
                presupuestos_mensuales = PresupuestoMensual.objects.filter(
                    mes__year=mes.year,
                    mes__month=mes.month
                )
                total_planificado = PresupuestoMensual.objects.filter(
                    mes__year=ahora.year,
                    mes__month=mes.month
                ).aggregate(Sum('planificado'))
                total_actual = PresupuestoMensual.objects.filter(
                    mes__year=ahora.year,
                    mes__month=mes.month
                ).aggregate(Sum('actual'))
            else:
                presupuestos_mensuales = PresupuestoMensual.objects.filter(
                    mes__year=ahora.year,
                    mes__month=ahora.month
                )
        context = {
            'efectivo_saliente': efectivo_saliente,
            'efectivo_entrante': efectivo_entrante,
            'presupuestos_mensuales': presupuestos_mensuales,
            'presupuesto_form': presupuesto_form,
            'encabezado': encabezado,
            'filtro_form': filtro_form,
            'total_planificado': total_planificado,
            'total_actual': total_actual
        }
        return render(request, 'finanzas/presupuesto_mensual.html', context)


class ResumenTransacciones(View):
    def get_context_data(self, *args, **kwargs):
        transaccion_form = AgregarTransaccionForm()
        filtro_form = FechaRangoForm()
        cuenta = Cuenta.objects.get(slug=kwargs['cuenta'])
        hoy = datetime.datetime.today().strftime("%d-%m-%Y")

        treinta_dias_atras = datetime.datetime.today() + datetime.timedelta(-30)
        treinta_dias_atras = treinta_dias_atras.strftime("%d-%m-%Y")

        fecha_inicio = kwargs['fecha_inicio']
        fecha_fin = kwargs['fecha_fin']

        if all(fecha_inicio == 0 and fecha_fin == 0):
            transacciones = Transaccion.objects.filter(
                cuenta=cuenta,
                fecha__range=[treinta_dias_atras, hoy]).order_by('fecha', 'id')
            transacciones_totales = Transaccion.objects.filter(
                cuenta=cuenta,
                fecha__gte=treinta_dias_atras).order_by('fecha', 'id').reverse()
        else:
            transacciones = Transaccion.objects.filter(
                cuenta=cuenta,
                fecha__range=[fecha_inicio, fecha_fin]).order_by('fecha', 'id')
            transacciones_totales = Transaccion.objects.filter(
                cuenta=cuenta,
                fecha__gte=fecha_inicio).order_by('fecha', 'id').reverse()

        balances = {}
        balance = cuenta.balance

        for item in transacciones_totales:
            balances[item.id] = balance
            # if item.debito == True:
            if item.debito:
                balance += item.monto
            # elif item.debito == False:
            elif not item.debito:
                balance -= item.monto

        context = {
            'balances': balances,
            'cuenta': cuenta,
            'filtro_form': filtro_form,
            'transaccion_form': transaccion_form,
            'transacciones': transacciones
        }
        return context

    def get(self, request, cuenta):
        fecha_inicio = 0
        fecha_fin = 0
        return render(request, 'finanzas/resumen_transacciones.html', self.get_context_data(
            request,
            cuenta=cuenta,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        ))

    def post(self, request, cuenta):
        pass
