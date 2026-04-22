from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings

from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token
from google.auth.transport import requests

from .models import (
    Producto,
    Categoria,
    Carrito,
    ItemCarrito,
    Pedido,
    ItemPedido,
    VarianteProducto
)

from .serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    CarritoSerializer,
    UserSerializer,
    ItemCarritoSerializer,
    PedidoSerializer,
)

from .filters import ProductoFilter


# ------------------------------------------------------------
# PRODUCTO
# ------------------------------------------------------------
class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    filterset_class = ProductoFilter

    def get_queryset(self):
        return Producto.objects.all().prefetch_related(
            'imagenes',              # imágenes del producto
            'variantes',             # variantes
            'variantes__imagenes'    # 🔥 imágenes de cada variante
        )


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


# ------------------------------------------------------------
# AGREGAR AL CARRITO
# ------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_al_carrito(request):
    producto_id = request.data.get('producto_id')
    variante_id = request.data.get('variante_id')
    cantidad = int(request.data.get('cantidad', 1))

    if not variante_id:
        return Response({'error': 'Debes seleccionar una variante'}, status=400)

    try:
        producto = Producto.objects.get(id=producto_id)
        variante = VarianteProducto.objects.get(id=variante_id, producto=producto)
    except:
        return Response({'error': 'Producto o variante no válida'}, status=404)

    if cantidad > variante.stock:
        return Response({'error': f'Solo hay {variante.stock} disponibles'}, status=400)

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        variante=variante,
        defaults={'cantidad': cantidad}
    )

    if not creado:
        nueva_cantidad = item.cantidad + cantidad

        if nueva_cantidad > variante.stock:
            return Response({'error': 'Stock insuficiente'}, status=400)

        if nueva_cantidad <= 0:
            item.delete()
            return Response({'message': 'Eliminado'}, status=200)

        item.cantidad = nueva_cantidad
        item.save()

    return Response(ItemCarritoSerializer(item).data, status=201)


# ------------------------------------------------------------
# ELIMINAR ITEM
# ------------------------------------------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_del_carrito(request, item_id):
    try:
        item = ItemCarrito.objects.get(id=item_id, carrito__usuario=request.user)
        item.delete()
        return Response({'message': 'Eliminado'}, status=200)
    except ItemCarrito.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)


# ------------------------------------------------------------
# ACTUALIZAR CANTIDAD
# ------------------------------------------------------------
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_cantidad_carrito(request, item_id):
    try:
        cantidad = int(request.data.get('cantidad', 1))
        item = ItemCarrito.objects.get(id=item_id, carrito__usuario=request.user)
    except:
        return Response({'error': 'Error'}, status=400)

    if cantidad <= 0:
        item.delete()
        return Response({'message': 'Eliminado'}, status=200)

    if cantidad > item.variante.stock:
        return Response({'error': f'Solo hay {item.variante.stock} disponibles'}, status=400)

    item.cantidad = cantidad
    item.save()
    return Response(ItemCarritoSerializer(item).data)


# ------------------------------------------------------------
# CARRITO
# ------------------------------------------------------------
class CarritoView(generics.RetrieveAPIView):
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito


# ------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
    })


# ------------------------------------------------------------
# CREAR PEDIDO 🔥
# ------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_pedido(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = list(carrito.items.select_related('producto', 'variante'))

    if not items:
        return Response({'error': 'Carrito vacío'}, status=400)

    # Validar stock
    for it in items:
        if it.variante.stock < it.cantidad:
            return Response({
                'error': f'Stock insuficiente para {it.producto.nombre}'
            }, status=400)

    with transaction.atomic():
        total = sum(
            (Decimal(it.variante.precio) * it.cantidad for it in items),
            Decimal('0')
        )

        pedido = Pedido.objects.create(usuario=request.user, total=total)

        for it in items:
            variante = it.variante
            variante.stock -= it.cantidad
            variante.save()

            ItemPedido.objects.create(
                pedido=pedido,
                producto=it.producto,
                variante=variante,
                cantidad=it.cantidad,
                precio_unitario=it.variante.precio
            )

        carrito.items.all().delete()

    return Response(PedidoSerializer(pedido).data, status=201)


# ------------------------------------------------------------
# LISTA PEDIDOS
# ------------------------------------------------------------
class PedidoPagination(PageNumberPagination):
    page_size = 10


class ListaPedidosUsuario(generics.ListAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PedidoPagination

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-id')


# ------------------------------------------------------------
# GOOGLE LOGIN
# ------------------------------------------------------------
@api_view(['POST'])
def google_login(request):
    token = request.data.get('token')

    if not token:
        return Response({'error': 'Token requerido'}, status=400)

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        email = idinfo.get('email')
        name = idinfo.get('name')

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': name or ''
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    except Exception:
        return Response({'error': 'Token inválido'}, status=400)
