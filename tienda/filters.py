import django_filters
from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    categoria = django_filters.NumberFilter(field_name='categoria__id')

    # ✅ FILTROS REALES
    talla = django_filters.CharFilter(field_name='variantes__talla', lookup_expr='iexact')
    color = django_filters.CharFilter(field_name='variantes__color', lookup_expr='iexact')

    class Meta:
        model = Producto
        fields = ['precio_min', 'precio_max', 'categoria', 'talla', 'color']
