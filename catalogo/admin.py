from django.contrib import admin

from .models import Autor, Editorial, Libro, Prestamo

# Register your models here

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "genero", "anio_publicacion", "disponible")
    list_filter = ("genero", "disponible")
    search_fields = ("titulo", "autores__nombre", "autores__apellidos", "isbn")
    ordering = ("titulo",)
    list_per_page = 5
    # filter_horizontal = ("autores",)
    
    # list_display = ("titulo", "isbn", "precio", "disponible", "editorial")
    # list_filter = ("disponible", "editorial")
    # search_fields = ("titulo", "isbn", "autores__nombre")

admin.site.register(Autor)
admin.site.register(Editorial)
admin.site.register(Prestamo)
