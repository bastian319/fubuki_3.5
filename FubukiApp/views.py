from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from pathlib import PureWindowsPath, PurePosixPath
from .forms import ResenaForm
from .models import Cliente, Resena, Producto

# Create your views here.
def index(request):
    return render(request, 'index.html', {
        'resenas': Resena.objects.all()[:2],
    })

def registrarse(request):
    if request.method == 'GET':
        return render(request, 'registrarse.html')
    else:
        # Recogemos los 3 datos del formulario HTML
        nombre_usuario = request.POST.get('nombre_usuario')
        correo = request.POST.get('correo')
        contrasena1 = request.POST.get('contrasena1')
        contrasena2 = request.POST.get('contrasena2')

        # Validamos que las contraseñas coincidan
        if contrasena1 != contrasena2:
            return render(request, 'registrarse.html', {
                'error': 'Las contraseñas no coinciden'
            })

        try:
            # Crear usuario de autenticación de Django usando el correo como nombre
            user = User.objects.create_user(username=correo, email=correo, password=contrasena1)
            user.save()

            # Guardamos los datos en modelo Cliente 
            Cliente.objects.create(
                nombre_usuario=nombre_usuario,
                correo=correo,
                contrasena=contrasena1 
            )

            #Inicio de sesión automatica
            login(request, user)
            return redirect('index')

        except IntegrityError:
            return render(request, 'registrarse.html', {
                'error': 'Este correo ya está registrado.'
            })
   
def productos(request):
    # productos listados
    lista_productos = Producto.objects.all()
    for producto in lista_productos:
        producto.imagen_url = _imagen_producto(producto.imagen)
    return render(request, 'productos.html', {'productos': lista_productos})

def promociones(request):
    return render(request, 'promociones.html')

def resenas(request):
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias! Tu reseña quedó publicada.')
            return redirect('resenas')
    else:
        form = ResenaForm()

    return render(request, 'resenas.html', {
        'form': form,
        'resenas': Resena.objects.all(),
    })


#Productos vista unica
def detalle_producto(request, producto_id):
    # Busca el producto por ID o lanza un error 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)
    producto.imagen_url = _imagen_producto(producto.imagen)
    
#   #definir tope de compra
    limite_compra_maximo = 50
    
    #definir el tope en base si el stock es menor o si el limite es menor al stock
    tope_maximo = min(producto.stock, limite_compra_maximo)
    
    return render(request, 'detalle_producto.html', {
        'producto': producto,
        'tope_maximo': tope_maximo
    })
    
def _imagen_producto(ruta):
    """Devuelve la ruta estática del nombre de imagen, incluso si la BD guarda una ruta absoluta."""
    if not ruta:
        return 'img/mochi.png'
    nombre = PureWindowsPath(str(ruta)).name
    nombre = PurePosixPath(nombre).name
    return f'img/{nombre}'


@require_POST
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1
    if cantidad < 1 or producto.stock < 1:
        messages.error(request, 'La cantidad indicada no es válida o el producto no tiene stock.')
        return redirect('detalle_producto', producto_id=producto.id)

    carrito = request.session.get('carrito', {})
    id_producto = str(producto.id)
    cantidad_actual = int(carrito.get(id_producto, 0))
    if cantidad_actual + cantidad > producto.stock:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
    else:
        carrito[id_producto] = cantidad_actual + cantidad
        request.session['carrito'] = carrito
        messages.success(request, f'{producto.nombre} se agregó al carrito.')
    return redirect('carrito')


@require_POST
def actualizar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    id_producto = str(producto_id)
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1
    if cantidad <= 0:
        carrito.pop(id_producto, None)
    elif cantidad > producto.stock:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
    else:
        carrito[id_producto] = cantidad
    request.session['carrito'] = carrito
    return redirect('carrito')


@require_POST
def quitar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('carrito')


def carrito(request):
    carrito_sesion = request.session.get('carrito', {})
    items = []
    subtotal = 0
    carrito_actualizado = {}
    for producto in Producto.objects.filter(id__in=carrito_sesion.keys()):
        cantidad = int(carrito_sesion.get(str(producto.id), 0))
        if cantidad <= 0 or producto.stock <= 0:
            continue
        cantidad = min(cantidad, producto.stock)
        carrito_actualizado[str(producto.id)] = cantidad
        total_item = producto.precio * cantidad
        subtotal += total_item
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'total': total_item,
            'imagen_url': _imagen_producto(producto.imagen),
        })
    request.session['carrito'] = carrito_actualizado
    return render(request, 'carrito.html', {'items': items, 'subtotal': subtotal, 'total': subtotal})
