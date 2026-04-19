from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
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
    TipoAtributo,
    ValorAtributo
)

# ------------------------------------------------------------
# 🔥 FORMSET PARA VALIDAR VARIANTES (CLAVE)
# ------------------------------------------------------------
class VarianteInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            atributos = form.cleaned_data.get("atributos")

            if not atributos:
                continue

            tipos = []

            for atributo in atributos:
                if atributo.tipo in tipos:
                    raise ValidationError(
                        "No puedes seleccionar dos valores del mismo tipo (ej: Color Azul y Color Café)."
                    )
                tipos.append(atributo.tipo)


# ------------------------------------------------------------
# 🔥 INLINE VARIANTES (CORRECTO)
# ------------------------------------------------------------
class VarianteInline(admin.StackedInline):
    model = VarianteProducto
    formset = VarianteInlineFormSet
    extra = 0
    filter_horizontal = ('atributos',)


# ------------------------------------------------------------
# 🖼️ INLINE IMÁGENES
# ------------------------------------------------------------
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


# ------------------------------------------------------------
# 🔥 FILTRO STOCK
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
# 📂 CATEGORÍA
# ------------------------------------------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ["nombre"]


# ------------------------------------------------------------
# 🔥 TIPO ATRIBUTO
# ------------------------------------------------------------
@admin.register(TipoAtributo)
class TipoAtributoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ["nombre"]


# ------------------------------------------------------------
# 🔥 VALOR ATRIBUTO
# ------------------------------------------------------------
@admin.register(ValorAtributo)
class ValorAtributoAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "valor")
    list_filter = ("tipo",)
    search_fields = ["valor"]


# ------------------------------------------------------------
# 🛍️ PRODUCTO
# ------------------------------------------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock_total', 'fecha_creacion', 'categoria')
    search_fields = ['nombre', 'categoria__nombre']
    list_filter = ['fecha_creacion', 'categoria', StockBajoFilter, FechaCreacionFilter]

    inlines = [VarianteInline, ProductoImagenInline]

    def stock_total(self, obj):
        return sum(v.stock for v in obj.variantes.all())

    stock_total.short_description = "Stock total"


# ------------------------------------------------------------
# 🛒 CARRITO
# ------------------------------------------------------------
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ('producto', 'variante', 'cantidad')


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
    readonly_fields = ('producto', 'variante', 'cantidad', 'precio_unitario')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'fecha')
    inlines = [ItemPedidoInline]
    search_fields = ['usuario__username']
    list_filter = ['fecha']
