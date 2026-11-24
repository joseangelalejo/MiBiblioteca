from django.shortcuts import get_object_or_404, render
from . import prestamos
from .models import Libro, Autor, Editorial, Prestamo
from django.db.models import Prefetch

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


def prestar_libro(request, pk_libro, pk_usuario):
    """Presta el libro `pk_libro` al usuario `pk_usuario` (la lógica está en `prestamos.py`)."""
    usuario = get_object_or_404(get_user_model(), pk=pk_usuario)
    try:
        prestamo = prestamos.prestar_libro(pk_libro, usuario)
    except Libro.DoesNotExist:
        raise Http404("El libro no existe")
    except ValueError as error:
        return HttpResponse(str(error), status=409)
    return HttpResponse(f"Préstamo {prestamo.pk} realizado correctamente")


def devolver_libro(request, pk_prestamo):
    """Registra la devolución del préstamo `pk_prestamo`."""
    try:
        prestamos.devolver_libro(pk_prestamo)
    except Prestamo.DoesNotExist:
        raise Http404("El préstamo no existe")
    except ValueError as error:
        return HttpResponse(str(error), status=409)
    return HttpResponse("Préstamo devuelto correctamente")
