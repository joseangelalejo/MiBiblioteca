from django.contrib import admin

from .models import Autor, Editorial, Libro

# Register your models here

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "genero", "anio_publicacion", "disponible")
    list_filter = ("genero", "disponible")
    search_fields = ("titulo", "autores__nombre", "autores__apellidos", "isbn")

admin.site.register(Autor)
admin.site.register(Editorial)