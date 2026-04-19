import django_filters
from .models import Producto

class ProductoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')

    categoria = django_filters.NumberFilter(field_name='categoria__id')

    # 🔥 FILTRO POR TALLA
    talla = django_filters.CharFilter(field_name='variantes__talla')

    class Meta:
        model = Producto
        fields = ['precio_min', 'precio_max', 'categoria', 'talla']
