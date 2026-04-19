from django.contrib import admin
from .models import Producto, ProductoImagen, Categoria, Carrito, ItemCarrito, Pedido, ItemPedido
from datetime import datetime, timedelta

class StockBajoFilter(admin.SimpleListFilter):
    title = 'Stock'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return [
            ('bajo', 'Stock bajo (≤5)'),
            ('sin_stock', 'Sin stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'bajo':
            return queryset.filter(stock__lte=5, stock__gt=0)
        if self.value() == 'sin_stock':
            return queryset.filter(stock=0)
        return queryset


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


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ["nombre"]


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'fecha_creacion', 'categoria')
    search_fields = ['nombre']
    list_filter = ['fecha_creacion', 'categoria', StockBajoFilter, FechaCreacionFilter]
    inlines = [ProductoImagenInline]  


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'creado')
    inlines = [ItemCarritoInline]
    search_fields = ['usuario__username']
    list_filter = ['creado']


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha')
    inlines = [ItemPedidoInline]
    search_fields = ['usuario__username']
    list_filter = ['fecha']

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
