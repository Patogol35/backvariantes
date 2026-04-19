import django_filters
from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    categoria = django_filters.NumberFilter(field_name='categoria__id')

    talla = django_filters.CharFilter(method='filter_talla')
    color = django_filters.CharFilter(method='filter_color')

    class Meta:
        model = Producto
        fields = ['precio_min', 'precio_max', 'categoria', 'talla', 'color']

    # 🔥 FILTRO TALLA SIN DUPLICADOS
    def filter_talla(self, queryset, name, value):
        return queryset.filter(variantes__talla=value).distinct()

    # 🔥 FILTRO COLOR SIN DUPLICADOS
    def filter_color(self, queryset, name, value):
        return queryset.filter(variantes__color=value).distinct()