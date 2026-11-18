"""Actividad 6. Comportamiento de on_delete al eliminar una editorial.

Está pensado para ejecutarse en una COPIA del proyecto con su propia base de
datos (ver Actividad6.md). Con PROTECT, que es lo que hay en `main`, no elimina
nada: solo muestra el ProtectedError. Con SET_NULL (editando Libro.editorial en
la copia) elimina la editorial y deja sus libros sin editorial.
Ejecución:
    python manage.py shell < actividad6_on_delete.py
"""
from django.db.models import ProtectedError

from catalogo.models import Editorial, Libro

editorial = Editorial.objects.get(nombre="Editorial Horizonte")
regla = Libro._meta.get_field("editorial").remote_field.on_delete.__name__
ids = list(editorial.libros.values_list("pk", flat=True))
print(f"on_delete actual: {regla}")
print(f"Libros de {editorial}: {len(ids)}")

try:
    editorial.delete()
except ProtectedError:
    print("ProtectedError: la editorial no se elimina y sus libros no cambian")
else:
    print("La editorial se ha eliminado")
    sin_editorial = Libro.objects.filter(pk__in=ids, editorial__isnull=True).count()
    print(f"Libros que conservan su fila y se quedan sin editorial: {sin_editorial}")

print(f"Libros en total: {Libro.objects.count()}")
print(f"Editoriales: {Editorial.objects.count()}")
