from django.contrib import admin

from .models import (Categoria, Cuenta, Presupuesto, PresupuestoMensual,
                     Transaccion)


class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'fecha', 'cuenta', 'monto')


admin.site.register(Transaccion, TransaccionAdmin)
admin.site.register(Categoria)
admin.site.register(Cuenta)
admin.site.register(Presupuesto)
admin.site.register(PresupuestoMensual)
