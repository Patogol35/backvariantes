import django_filters
from .models import Producto


class ProductoFilter(django_filters.FilterSet):

    # 🔥 FILTRO POR PRECIO (VARIANTES)
    precio_min = django_filters.NumberFilter(
        field_name='variantes__precio',
        lookup_expr='gte'
    )
    precio_max = django_filters.NumberFilter(
        field_name='variantes__precio',
        lookup_expr='lte'
    )

    # 📂 CATEGORÍA
    categoria = django_filters.NumberFilter(field_name='categoria__id')

    # 🎯 VARIANTES
    talla = django_filters.CharFilter(field_name='variantes__talla', lookup_expr='iexact')
    color = django_filters.CharFilter(field_name='variantes__color', lookup_expr='iexact')
    capacidad = django_filters.CharFilter(field_name='variantes__capacidad', lookup_expr='iexact')
    modelo = django_filters.CharFilter(field_name='variantes__modelo', lookup_expr='iexact')

    class Meta:
        model = Producto
        fields = [
            'precio_min',
            'precio_max',
            'categoria',
            'talla',
            'color',
            'capacidad',
            'modelo'
        ]
