"""Actividad 6. Consultas ORM sobre modelos relacionados.

Consultas resueltas sin SQL directo, con el ORM de Django.
Preparación:
    python manage.py shell < cargar_libros.py
    python manage.py shell < actividad6_datos.py
Ejecución:
    python manage.py shell < actividad6_consultas.py

Nota: Libro.editorial tiene related_name="libros" y Libro.autores también, así
que desde Editorial y desde Autor se accede a sus libros con ".libros".
"""
from django.db import connection
from django.db.models import Count, ProtectedError, Prefetch
from django.test.utils import CaptureQueriesContext

from catalogo.models import Autor, Editorial, Libro

horizonte = Editorial.objects.get(nombre="Editorial Horizonte")
del_sur = Editorial.objects.get(nombre="Ediciones del Sur")
neruda = Autor.objects.get(nombre="Pablo", apellidos="Neruda")
libro_dos_autores = Libro.objects.get(isbn="9780000000073")


def titulos(libros):
    return ", ".join(libro.titulo for libro in libros)


# 8. Todos los libros de una editorial (desde Libro, con el campo editorial)
print("\n--- 8. Libros de Editorial Horizonte ---")
print(f"  {titulos(Libro.objects.filter(editorial=horizonte))}")

# 9. Todos los libros de un autor (desde Libro, con el campo autores)
print("\n--- 9. Libros de Pablo Neruda ---")
print(f"  {titulos(Libro.objects.filter(autores=neruda))}")

# 10. Todos los autores de un libro
print(f"\n--- 10. Autores de {libro_dos_autores.titulo} ---")
print(f"  {', '.join(str(a) for a in libro_dos_autores.autores.all())}")

# 11. Contar los libros de cada editorial con annotate() (Count sobre related_name)
print("\n--- 11. Libros por editorial ---")
for editorial in Editorial.objects.annotate(total=Count("libros")).order_by("nombre"):
    print(f"  {editorial.nombre}: {editorial.total}")

# 12. Intentar eliminar una editorial con libros: PROTECT lo impide
print("\n--- 12. Eliminar una editorial con libros (PROTECT) ---")
try:
    horizonte.delete()
except ProtectedError as error:
    print(f"  ProtectedError: no se elimina {horizonte}; hay {len(error.protected_objects)} libros que la protegen")
print(f"  La editorial sigue existiendo: {Editorial.objects.filter(pk=horizonte.pk).exists()}")

# 13. related_name: desde la editorial y desde el autor con ".libros"
print("\n--- 13. Consultas con related_name ---")
print(f"  horizonte.libros.all(): {titulos(horizonte.libros.all())}")
print(f"  neruda.libros.all(): {titulos(neruda.libros.all())}")
print(
    "  Editoriales con algún libro disponible: "
    f"{', '.join(e.nombre for e in Editorial.objects.filter(libros__disponible=True).distinct())}"
)


def recorrer(libros):
    """Lee la editorial y los autores de cada libro, como haría una plantilla."""
    for libro in libros:
        _ = libro.editorial
        _ = list(libro.autores.all())


# 14 y 16. select_related() y prefetch_related(): comparar las consultas SQL
print("\n--- 14 y 16. Consultas SQL antes y después de optimizar ---")
with CaptureQueriesContext(connection) as sin_optimizar:
    recorrer(Libro.objects.all())
with CaptureQueriesContext(connection) as optimizado:
    recorrer(Libro.objects.select_related("editorial").prefetch_related("autores"))
print(f"  Sin optimizar: {len(sin_optimizar)} consultas")
print(f"  Con select_related('editorial') y prefetch_related('autores'): {len(optimizado)} consultas")
for consulta in optimizado.captured_queries:
    print(f"    {consulta['sql'][:110]}...")

print("\n--- 14. Libros con su editorial y sus autores ---")
libros = Libro.objects.select_related("editorial").prefetch_related("autores")
for libro in libros.filter(editorial__isnull=False):
    autores = ", ".join(str(a) for a in libro.autores.all())
    print(f"  {libro.titulo} | {libro.editorial} | {autores}")

# 15. Prefetch: solo los libros disponibles de cada editorial
print("\n--- 15. Libros disponibles de cada editorial (Prefetch) ---")
editoriales = Editorial.objects.prefetch_related(
    Prefetch(
        "libros",
        queryset=Libro.objects.filter(disponible=True),
        to_attr="libros_disponibles",
    )
).order_by("nombre")
for editorial in editoriales:
    print(f"  {editorial.nombre}: {titulos(editorial.libros_disponibles)}")
