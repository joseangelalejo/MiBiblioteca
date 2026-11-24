from django.shortcuts import get_object_or_404, render
from .models import Libro, Autor, Editorial, Prestamo
from django.db.models import Prefetch
from django.utils import timezone

from django.db import transaction
from django.contrib.auth import get_user_model
from django.http import HttpResponse

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
    with transaction.atomic():
        libro = Libro.objects.select_for_update().get(pk=pk_libro)
        if not libro.disponible:
            raise ValueError("El libro no está disponible")

        usuario = get_user_model().objects.select_for_update().get(pk=pk_usuario)

        prestamo = Prestamo.objects.create(
            libro=libro,
            usuario=usuario,
        )
        libro.disponible = False
        libro.save(update_fields=["disponible"])
        return HttpResponse("Préstamo realizado correctamente")

def devolver_libro(request, pk_prestamo):
    with transaction.atomic():
        prestamo = Prestamo.objects.select_for_update().get(pk=pk_prestamo)
        if prestamo.fecha_devolucion is not None:
            raise ValueError("El préstamo ya fue devuelto")

        prestamo.fecha_devolucion = timezone.now()
        prestamo.save(update_fields=["fecha_devolucion"])
        # raise RuntimeError("Error simulado")
        prestamo.libro.disponible = True
        prestamo.libro.save(update_fields=["disponible"])
        return HttpResponse("Préstamo devuelto correctamente")