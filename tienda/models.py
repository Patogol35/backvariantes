from django.db import models
from django.contrib.auth.models import User


# ------------------------------------------------------------
# CATEGORÍA
# ------------------------------------------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------
# PRODUCTO
# ------------------------------------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.URLField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------
# VARIANTES 🔥
# ------------------------------------------------------------
class VarianteProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        related_name="variantes",
        on_delete=models.CASCADE
    )

    talla = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    # 🔥 NUEVOS CAMPOS
    material = models.CharField(max_length=50, blank=True, null=True)
    edicion = models.CharField(max_length=50, blank=True, null=True)

    # 🔥 TECNOLOGÍA
    capacidad = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)

    # 🔥 PRECIO POR VARIANTE
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'producto',
                    'talla',
                    'color',
                    'material',
                    'edicion',
                    'capacidad',
                    'marca'
                ],
                name='unique_producto_variante'
            )
        ]

    def __str__(self):
        atributos = [
            self.talla,
            self.color,
            self.material,
            self.edicion,
            self.capacidad,
            self.marca
        ]

        atributos = [a for a in atributos if a]

        return f"{self.producto.nombre} - {' / '.join(atributos) if atributos else 'Variante'}"


# ------------------------------------------------------------
# IMÁGENES
# ------------------------------------------------------------
class ProductoImagen(models.Model):
    producto = models.ForeignKey(
        Producto,
        related_name='imagenes',
        on_delete=models.CASCADE
    )

    variante = models.ForeignKey(
        VarianteProducto,
        related_name='imagenes',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    imagen = models.URLField(max_length=500)

    def __str__(self):
        if self.variante:
            return f"Imagen de {self.producto.nombre} ({self.variante})"
        return f"Imagen de {self.producto.nombre}"


# ------------------------------------------------------------
# CARRITO
# ------------------------------------------------------------
class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Carrito de {self.usuario.username}'


# ------------------------------------------------------------
# ITEM CARRITO
# ------------------------------------------------------------
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.variante:
            return f'{self.cantidad} x {self.producto.nombre} ({self.variante})'
        return f'{self.cantidad} x {self.producto.nombre}'

    def subtotal(self):
        precio = self.variante.precio if self.variante and self.variante.precio else self.producto.precio
        return self.cantidad * precio


# ------------------------------------------------------------
# PEDIDO
# ------------------------------------------------------------
class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'


# ------------------------------------------------------------
# ITEM PEDIDO
# ------------------------------------------------------------
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        if self.variante:
            return f'{self.cantidad} x {self.producto.nombre} ({self.variante})'
        return f'{self.cantidad} x {self.producto.nombre}'
