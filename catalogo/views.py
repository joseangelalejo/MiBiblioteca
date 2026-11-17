from django.shortcuts import get_object_or_404, render
from .models import Libro, Autor, Editorial

# Create your views here.

def lista_libros(request):
    libros = Libro.objects.order_by("titulo")
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
    return render(request, "catalogo/lista_editoriales.html", {"editorial": editorial, "libros": libros, "cantidad_libros": cantidad_libros})