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
    VarianteProducto,
    VarianteImagen
)

# ------------------------------------------------------------
# 🔥 FILTRO STOCK (VARIANTES)
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
# 🖼️ INLINE IMÁGENES PRODUCTO
# ------------------------------------------------------------
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1

# ------------------------------------------------------------
# 🔥 INLINE IMÁGENES VARIANTE
# ------------------------------------------------------------
class VarianteImagenInline(admin.TabularInline):
    model = VarianteImagen
    extra = 1

# ------------------------------------------------------------
# 🧩 INLINE VARIANTES
# ------------------------------------------------------------
class VarianteInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1
    fields = ('talla', 'color', 'modelo', 'capacidad', 'precio', 'stock')
    show_change_link = True  # 🔥 permite ir a editar la variante

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
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion', 'categoria', 'precio_min', 'precio_max')
    search_fields = ['nombre']
    list_filter = ['fecha_creacion', 'categoria', StockBajoFilter, FechaCreacionFilter]

    inlines = [VarianteInline, ProductoImagenInline]

    def precio_min(self, obj):
        precios = [p for p in obj.variantes.values_list('precio', flat=True) if p is not None]
        return min(precios) if precios else 0
    precio_min.short_description = "Precio mínimo"

    def precio_max(self, obj):
        precios = [p for p in obj.variantes.values_list('precio', flat=True) if p is not None]
        return max(precios) if precios else 0
    precio_max.short_description = "Precio máximo"

# ------------------------------------------------------------
# 🔥 VARIANTE (AQUÍ EDITAS SUS IMÁGENES)
# ------------------------------------------------------------
@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'talla', 'color', 'modelo', 'precio', 'stock')
    search_fields = ['producto__nombre', 'color', 'modelo']
    list_filter = ['producto', 'color']

    inlines = [VarianteImagenInline]

# ------------------------------------------------------------
# 🛒 CARRITO
# ------------------------------------------------------------
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0

@admin.register(Carrito)
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

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'total')
    inlines = [ItemPedidoInline]
    search_fields = ['usuario__username']
    list_filter = ['fecha']