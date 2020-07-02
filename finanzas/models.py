import datetime

from django.db import models
from django.utils.text import slugify


class Cuenta(models.Model):
    balance = models.IntegerField('balance')
    nombre = models.CharField('nombre', max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Cuenta, self).save(*args, **kwargs)


class Presupuesto(models.Model):
    nombre = models.CharField('nombre', max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Presupuesto, self).save(*args, **kwargs)


class PresupuestoMensual(models.Model):
    actual = models.IntegerField('actual')
    mes = models.DateField('mes')
    planificado = models.IntegerField('planificado')
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Presupuesto Mensual'
        verbose_name_plural = 'Presupuestos Mensuales'

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.presupuesto}-{self.mes}")
        super(PresupuestoMensual, self).save(*args, **kwargs)


class Categoria(models.Model):
    nombre = models.CharField('nombre', max_length=50)
    prespuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Categoria, self).save(*args, **kwargs)


class Transaccion(models.Model):
    balance = models.IntegerField('balance')
    beneficiario = models.CharField('beneficiario', max_length=50)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, blank=True, null=True)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    debito = models.BooleanField('débito', default=True)
    fecha = models.DateField('fecha')
    monto = models.IntegerField('monto')
    presupuesto = models.ForeignKey(
        PresupuestoMensual, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True)
    transferencia = models.BooleanField('transferencia', default=False)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        time = datetime.datetime.now().time().strftime("%H%M%S")
        slug = f"{self.fecha}-{time}-{self.cuenta}-{self.monto}"
        self.slug = slugify(slug)
        super(Transaccion, self).save(*args, **kwargs)
