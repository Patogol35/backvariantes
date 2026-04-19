from rest_framework import serializers
from .models import (
    Producto,
    Categoria,
    ProductoImagen,
    VarianteProducto,
    Carrito,
    ItemCarrito,
    Pedido,
    ItemPedido
)
from django.contrib.auth.models import User

# ------------------------------------------------------------
# CATEGORÍA
# ------------------------------------------------------------
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"

# ------------------------------------------------------------
# VARIANTE 🔥
# ------------------------------------------------------------
class VarianteProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VarianteProducto
        fields = [
            'id',
            'talla',
            'color',
            'modelo',
            'capacidad',
            'precio',
            'stock'
        ]

# ------------------------------------------------------------
# IMÁGENES
# ------------------------------------------------------------
class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = ['imagen']

# ------------------------------------------------------------
# PRODUCTO
# ------------------------------------------------------------
class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source="categoria",
        write_only=True
    )

    imagenes = ProductoImagenSerializer(many=True, read_only=True)
    variantes = VarianteProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = "__all__"

# ------------------------------------------------------------
# ITEM CARRITO
# ------------------------------------------------------------
class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    variante = VarianteProductoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'variante', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return obj.cantidad * obj.variante.precio

# ------------------------------------------------------------
# CARRITO
# ------------------------------------------------------------
class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'creado', 'items']

# ------------------------------------------------------------
# USUARIO
# ------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False}
        }

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return email

    def validate_password(self, password):
        if len(password) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Debe incluir al menos un número.")
        if not any(not char.isalnum() for char in password):
            raise serializers.ValidationError("Debe incluir al menos un símbolo.")
        return password

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].strip().lower()
        return User.objects.create_user(**validated_data)

# ------------------------------------------------------------
# ITEM PEDIDO
# ------------------------------------------------------------
class ItemPedidoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    variante = VarianteProductoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemPedido
        fields = ['producto', 'variante', 'cantidad', 'precio_unitario', 'subtotal']

    def get_subtotal(self, obj):
        return obj.cantidad * obj.precio_unitario

# ------------------------------------------------------------
# PEDIDO
# ------------------------------------------------------------
class PedidoSerializer(serializers.ModelSerializer):
    items = ItemPedidoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'fecha', 'total', 'items']
