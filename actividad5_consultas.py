"""Actividad 5. Boletín de consultas ORM.

Consultas resueltas sin SQL directo, con el ORM de Django.
Preparación: tener al menos diez libros en la base de datos, por ejemplo con
    python manage.py shell < cargar_libros.py
Ejecución:
    python manage.py shell < actividad5_consultas.py

Nota: el modelo Libro define Meta.ordering = ["titulo"], así que las consultas
sin order_by() devuelven los libros ordenados por título.
"""
from django.db.models import Avg, Count, Max, Min, Q

from catalogo.models import Libro


def mostrar(titulo, libros):
    """Imprime el título de la consulta y sus resultados."""
    libros = list(libros)
    print(f"\n--- {titulo} ---")
    for libro in libros:
        print(
            f"  {libro.titulo} | {libro.precio} € | {libro.fecha_publicacion} | "
            f"{libro.paginas} págs. | disponible={libro.disponible}"
        )
    print(f"  ({len(libros)} resultado(s))")


if Libro.objects.count() < 10:
    print("AVISO: la actividad requiere al menos diez libros; carga cargar_libros.py")

# 1. Mostrar todos los libros
mostrar("1. Todos los libros", Libro.objects.all())

# 2. Obtener los libros disponibles
mostrar("2. Libros disponibles", Libro.objects.filter(disponible=True))

# 3. Obtener los libros no disponibles
mostrar("3. Libros no disponibles", Libro.objects.filter(disponible=False))

# 4. Título que contenga "python", sin distinguir mayúsculas (icontains)
mostrar(
    '4. Título con "python" (sin distinguir mayúsculas)',
    Libro.objects.filter(titulo__icontains="python"),
)

# 5. Precio superior a 20 euros (gt = mayor que)
mostrar("5. Precio superior a 20 €", Libro.objects.filter(precio__gt=20))

# 6. Precio entre 10 y 30 euros, ambos incluidos (range es inclusivo)
mostrar(
    "6. Precio entre 10 y 30 € (incluidos)",
    Libro.objects.filter(precio__range=(10, 30)),
)

# 7. Publicados a partir de 2023 (year__gte filtra por el año de la fecha)
mostrar(
    "7. Publicados a partir de 2023",
    Libro.objects.filter(fecha_publicacion__year__gte=2023),
)

# 8. Ordenados alfabéticamente por título
mostrar("8. Orden alfabético por título", Libro.objects.order_by("titulo"))

# 9. Ordenados por precio descendente (el signo "-" invierte el orden)
mostrar("9. Precio descendente", Libro.objects.order_by("-precio"))

# 10. Los tres libros más baratos (orden ascendente y slicing, LIMIT 3)
mostrar("10. Tres libros más baratos", Libro.objects.order_by("precio")[:3])

# 11. Disponibles con más de 250 páginas (varias condiciones = AND)
mostrar(
    "11. Disponibles con más de 250 páginas",
    Libro.objects.filter(disponible=True, paginas__gt=250),
)

# 12. Título con "python" O "django" (objetos Q combinados con |)
mostrar(
    '12. Título con "python" o "django"',
    Libro.objects.filter(
        Q(titulo__icontains="python") | Q(titulo__icontains="django")
    ),
)

# 13. Número total de libros
print("\n--- 13. Número total de libros ---")
print(f"  {Libro.objects.count()}")

# 14. Precio medio, máximo y mínimo (aggregate devuelve un diccionario)
print("\n--- 14. Precio medio, máximo y mínimo ---")
resumen = Libro.objects.aggregate(
    media=Avg("precio"), maximo=Max("precio"), minimo=Min("precio")
)
print(
    f"  media={round(resumen['media'], 2)} € | "
    f"máximo={round(resumen['maximo'], 2)} € | "
    f"mínimo={round(resumen['minimo'], 2)} €"
)

# 15. Agrupar por disponibilidad y contar los libros de cada grupo
#     (values() fija el grupo y annotate() calcula un valor por cada grupo)
print("\n--- 15. Libros por disponibilidad ---")
grupos = Libro.objects.values("disponible").annotate(total=Count("id"))
for grupo in grupos.order_by("-disponible"):
    estado = "disponibles" if grupo["disponible"] else "no disponibles"
    print(f"  {estado}: {grupo['total']}")

# Apoyo para las preguntas
print("\n=== Apoyo para las preguntas ===")

# filter() no falla si no encuentra registros: devuelve un QuerySet vacío
print("filter() sin coincidencias:", Libro.objects.filter(titulo__icontains="zzz"))

# values() devuelve un QuerySet de diccionarios (no de objetos Libro)
print("values():", list(Libro.objects.values("titulo", "precio")[:2]))
