import django_filters
from .models import Producto

class ProductoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name='variantes__precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='variantes__precio', lookup_expr='lte')

    categoria = django_filters.NumberFilter(field_name='categoria__id')

    talla = django_filters.CharFilter(field_name='variantes__talla')
    color = django_filters.CharFilter(field_name='variantes__color')
    modelo = django_filters.CharFilter(field_name='variantes__modelo')
    capacidad = django_filters.CharFilter(field_name='variantes__capacidad')

    class Meta:
        model = Producto
        fields = ['precio_min', 'precio_max', 'categoria', 'talla', 'color', 'modelo', 'capacidad']
