from django.contrib import admin
from .models import (
    Producto,
    ProductoImagen,
    Categoria,
    Carrito,
    ItemCarrito,
    Pedido,
    ItemPedido,
    Variante
)
from datetime import datetime, timedelta


# =========================
# FILTRO STOCK (AHORA POR VARIANTE)
# =========================
class StockBajoFilter(admin.SimpleListFilter):
    title = 'Stock (variantes)'
    parameter_name = 'stock_variante'

    def lookups(self, request, model_admin):
        return [
            ('bajo', 'Stock bajo (≤5)'),
            ('sin_stock', 'Sin stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'bajo':
            return queryset.filter(variantes__stock__lte=5, variantes__stock__gt=0).distinct()
        if self.value() == 'sin_stock':
            return queryset.filter(variantes__stock=0).distinct()
        return queryset


# =========================
# FILTRO FECHA
# =========================
class FechaCreacionFilter(admin.SimpleListFilter):
    title = 'Fecha de creación'
    parameter_name = 'fecha_creacion_custom'

    def lookups(self, request, model_admin):
        return [
            ('hoy', 'Hoy'),
            ('semana', 'Esta semana'),
        ]

    def queryset(self, request, queryset):
        hoy = datetime.now().date()

        if self.value() == 'hoy':
            return queryset.filter(fecha_creacion__date=hoy)

        if self.value() == 'semana':
            semana_inicio = hoy - timedelta(days=hoy.weekday())
            return queryset.filter(fecha_creacion__date__gte=semana_inicio)

        return queryset


# =========================
# INLINES
# =========================
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


# =========================
# ADMIN CATEGORIA
# =========================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ["nombre"]


# =========================
# ADMIN PRODUCTO
# =========================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'fecha_creacion')
    search_fields = ['nombre']
    list_filter = ['categoria', StockBajoFilter, FechaCreacionFilter]
    inlines = [ProductoImagenInline, VarianteInline]


# =========================
# ADMIN CARRITO
# =========================
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'creado')
    inlines = [ItemCarritoInline]
    search_fields = ['usuario__username']
    list_filter = ['creado']


# =========================
# ADMIN PEDIDO
# =========================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'total')
    inlines = [ItemPedidoInline]
    search_fields = ['usuario__username']
    list_filter = ['fecha']
