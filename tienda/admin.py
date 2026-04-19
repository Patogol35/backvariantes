from django.contrib import admin
from datetime import datetime, timedelta

from .models import (
    Producto,
    ProductoImagen,
    Categoria,
    Carrito,
    ItemCarrito,
    Pedido,
    ItemPedido,
    VarianteProducto
)

# ------------------------------------------------------------
# 🔥 FILTRO STOCK (SOBRE VARIANTES)
# ------------------------------------------------------------
class StockBajoFilter(admin.SimpleListFilter):
    title = 'Stock (variantes)'
    parameter_name = 'stock_variantes'

    def lookups(self, request, model_admin):
        return [
            ('bajo', 'Stock bajo (≤5)'),
            ('sin_stock', 'Sin stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'bajo':
            return queryset.filter(
                variantes__stock__lte=5,
                variantes__stock__gt=0
            ).distinct()

        if self.value() == 'sin_stock':
            return queryset.filter(
                variantes__stock=0
            ).distinct()

        return queryset


# ------------------------------------------------------------
# 📅 FILTRO FECHA
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# 🧩 INLINE VARIANTES
# ------------------------------------------------------------
class VarianteInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1

    fields = (
        'talla',
        'color',
        'capacidad',
        'modelo',
        'precio',
        'stock'
    )


# ------------------------------------------------------------
# 🖼️ INLINE IMÁGENES
# ------------------------------------------------------------
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


# ------------------------------------------------------------
# 📂 CATEGORÍA
# ------------------------------------------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ["nombre"]


# ------------------------------------------------------------
# 🛍️ PRODUCTO
# ------------------------------------------------------------
class ProductoAdmin(admin.ModelAdmin):

    # 🔥 Precio mínimo entre variantes
    def precio_min(self, obj):
        variantes = obj.variantes.all()
        if variantes.exists():
            return min(v.precio for v in variantes)
        return obj.precio

    precio_min.short_description = "Precio desde"

    # 🔥 Stock total
    def stock_total(self, obj):
        return sum(v.stock for v in obj.variantes.all())

    stock_total.short_description = "Stock total"

    list_display = (
        'nombre',
        'precio_min',
        'stock_total',
        'fecha_creacion',
        'categoria'
    )

    search_fields = ['nombre']
    list_filter = ['categoria', StockBajoFilter, FechaCreacionFilter]

    inlines = [VarianteInline, ProductoImagenInline]


# ------------------------------------------------------------
# 🛒 CARRITO
# ------------------------------------------------------------
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    fields = ('producto', 'variante', 'cantidad')


class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'creado')
    inlines = [ItemCarritoInline]
    search_fields = ['usuario__username']
    list_filter = ['creado']


# ------------------------------------------------------------
# 📦 PEDIDOS
# ------------------------------------------------------------
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ('producto', 'variante', 'cantidad', 'precio_unitario')


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'total')
    inlines = [ItemPedidoInline]
    search_fields = ['usuario__username']
    list_filter = ['fecha']


# ------------------------------------------------------------
# 🚀 REGISTROS
# ------------------------------------------------------------
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
