from datetime import date
from decimal import Decimal

from django.shortcuts import get_object_or_404, render
from .models import Libro, Autor, Editorial, Prestamo
from django.db import transaction
from django.db.models import Avg, Count, Prefetch
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse

# Create your views here.

def lista_libros(request):
    libros = Libro.objects.order_by("titulo").prefetch_related("autores")
    return render(request, "catalogo/lista_libros.html", {"libros": libros})

def detalle_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    return render(request, "catalogo/detalle_libro.html", {"libro": libro})

def editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    
    return render(request, "catalogo/editorial.html", {"editorial": editorial})

def detalle_editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    
    return render(request, "catalogo/detalle_editorial.html", {"editorial": editorial})

def detalle_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    
    return render(request, "catalogo/detalle_autor.html", {"autor": autor})

def lista_editoriales(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    libros = Libro.objects.filter(editorial=editorial)
    cantidad_libros = libros.count()
    #editoriales = Editorial.objects.prefetch_related(
    #Prefetch(
    #    "libros",
    #    queryset=Libro.objects.filter(disponible=True),
    #    to_attr="libros_disponibles",
    #    )
    #).order_by("nombre")
    return render(request, "catalogo/lista_editoriales.html", {"editorial": editorial, "libros": libros, "cantidad_libros": cantidad_libros})


def prestar_libro(libro_id, usuario):
    """Registra un préstamo y marca el libro como no disponible."""
    with transaction.atomic():
        # select_for_update() bloquea la fila durante la transacción en gestores
        # compatibles (PostgreSQL). SQLite no bloquea filas.
        libro = Libro.objects.select_for_update().get(pk=libro_id)
        if not libro.disponible:
            raise ValueError("El libro no está disponible")

        prestamo = Prestamo.objects.create(libro=libro, usuario=usuario)
        libro.disponible = False
        libro.save(update_fields=["disponible"])
        return prestamo


def devolver_libro(prestamo_id):
    """Registra la fecha de devolución y vuelve a marcar el libro como disponible."""
    with transaction.atomic():
        prestamo = Prestamo.objects.select_for_update().get(pk=prestamo_id)
        if prestamo.fecha_devolucion is not None:
            raise ValueError("El préstamo ya fue devuelto")

        prestamo.fecha_devolucion = timezone.now()
        prestamo.save(update_fields=["fecha_devolucion"])
        prestamo.libro.disponible = True
        prestamo.libro.save(update_fields=["disponible"])
        return prestamo


def prestar_libro_vista(request, pk_libro, pk_usuario):
    """Presta el libro `pk_libro` al usuario `pk_usuario`."""
    usuario = get_object_or_404(get_user_model(), pk=pk_usuario)
    try:
        prestamo = prestar_libro(pk_libro, usuario)
    except Libro.DoesNotExist:
        raise Http404("El libro no existe")
    except ValueError as error:
        return HttpResponse(str(error), status=409)
    return HttpResponse(f"Préstamo {prestamo.pk} realizado correctamente")


def devolver_libro_vista(request, pk_prestamo):
    """Registra la devolución del préstamo `pk_prestamo`."""
    try:
        devolver_libro(pk_prestamo)
    except Prestamo.DoesNotExist:
        raise Http404("El préstamo no existe")
    except ValueError as error:
        return HttpResponse(str(error), status=409)
    return HttpResponse("Préstamo devuelto correctamente")

# ---------------------------------------------------------------------------
# Operaciones de gestión de la biblioteca
# No son vistas HTTP: son funciones que se llaman desde `python manage.py shell`
# (ejemplos en el README.md).
# ---------------------------------------------------------------------------

# --- Parte C: operaciones CRUD ---

def crear_editorial_y_autores():
    """Crea una editorial y dos autores de ejemplo (si no existen) y los devuelve."""
    nueva_editorial, _ = Editorial.objects.get_or_create(
        nombre="Editorial Demo",
        defaults={"email": "contacto@editorial-demo.example", "pais": "España"},
    )
    autor_uno, _ = Autor.objects.get_or_create(
        nombre="Ana", apellidos="Demo Uno", defaults={"nacionalidad": "Española"}
    )
    autor_dos, _ = Autor.objects.get_or_create(
        nombre="Luis", apellidos="Demo Dos", defaults={"nacionalidad": "Mexicana"}
    )
    return nueva_editorial, autor_uno, autor_dos


def crear_libro(titulo, isbn, precio, fecha_publicacion, editorial_id, autores, paginas=200):
    """Crea un libro con su editorial y sus autores (o lo devuelve si el ISBN ya existe)."""
    libro, creado = Libro.objects.get_or_create(
        isbn=isbn,
        defaults={
            "titulo": titulo,
            "precio": precio,
            "fecha_publicacion": fecha_publicacion,
            "anio_publicacion": fecha_publicacion.year,
            "paginas": paginas,
            "editorial_id": editorial_id,
        },
    )
    if creado:
        libro.autores.set(autores)
    return libro


def crear_tres_libros(nueva_editorial, autor_uno, autor_dos):
    """Crea tres libros de ejemplo y asigna a cada uno sus autores."""
    return [
        crear_libro("Libro Demo 1", "9780000001001", Decimal("12.50"),
                    date(2020, 1, 15), nueva_editorial.pk, [autor_uno]),
        crear_libro("Libro Demo 2", "9780000001002", Decimal("18.00"),
                    date(2021, 6, 1), nueva_editorial.pk, [autor_uno, autor_dos]),
        crear_libro("Libro Demo 3", "9780000001003", Decimal("9.90"),
                    date(2022, 9, 30), nueva_editorial.pk, [autor_dos]),
    ]


def libro_por_isbn(isbn):
    """Recupera un libro por su ISBN (lanza Libro.DoesNotExist si no existe)."""
    return Libro.objects.get(isbn=isbn)


def modificar_precio(isbn, nuevo_precio):
    """Cambia el precio de un libro. La base de datos rechaza precios negativos."""
    libro = Libro.objects.get(isbn=isbn)
    libro.precio = nuevo_precio
    libro.save(update_fields=["precio"])
    return libro


def eliminar_libro(isbn):
    """Elimina un libro si no tiene préstamos; si los tiene, lanza ValueError."""
    libro = Libro.objects.get(isbn=isbn)
    if libro.prestamos.exists():
        raise ValueError("El libro tiene préstamos asociados y no se puede eliminar")
    return libro.delete()


# --- Parte D: consultas ORM (sin SQL directo) ---

def libros_disponibles():
    return Libro.objects.filter(disponible=True).order_by("titulo")


def buscar_libros(texto):
    return Libro.objects.filter(titulo__icontains=texto).order_by("titulo")


def libros_de_editorial(editorial_id):
    return Libro.objects.filter(editorial_id=editorial_id).order_by("titulo")


def libros_de_autor(autor_id):
    return Libro.objects.filter(autores__id=autor_id).order_by("titulo")


def precio_medio():
    return Libro.objects.aggregate(precio_medio=Avg("precio"))["precio_medio"]


def libros_por_editorial():
    return Editorial.objects.annotate(total_libros=Count("libros")).order_by("nombre")


def prestamos_activos():
    return (
        Prestamo.objects.filter(fecha_devolucion__isnull=True)
        .select_related("libro", "usuario")
        .order_by("fecha_prestamo")
    )
