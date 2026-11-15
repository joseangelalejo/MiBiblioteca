"""Actividad 4. Gestión CRUD del catálogo.

Operaciones realizadas exclusivamente con el ORM de Django.
Ejecución: python manage.py shell < actividad4_crud.py
"""
from datetime import date
from decimal import Decimal

from catalogo.models import Libro

# ISBN de los cinco libros de esta actividad (ficticios y distintos entre sí)
ISBN_1 = "9780000001001"
ISBN_2 = "9780000001002"
ISBN_3 = "9780000001003"
ISBN_4 = "9780000001004"
ISBN_5 = "9780000001005"
ISBN_INEXISTENTE = "9780000009999"

# Limpieza previa de los libros de esta actividad, para poder repetir el script
# sin errores de ISBN duplicado. No toca ningún otro libro.
Libro.objects.filter(
    isbn__in=[ISBN_1, ISBN_2, ISBN_3, ISBN_4, ISBN_5]
).delete()

# 1. CREATE: crear cinco libros con ISBN distintos
print("\n=== 1. Crear cinco libros ===")
datos = [
    {
        "titulo": "Python para todos",
        "autor": "Ana Torres",
        "isbn": ISBN_1,
        "fecha_publicacion": date(2021, 3, 15),
        "paginas": 320,
        "precio": Decimal("22.50"),
    },
    {
        "titulo": "Django desde cero",
        "autor": "Luis Herrera",
        "isbn": ISBN_2,
        "fecha_publicacion": date(2022, 9, 1),
        "paginas": 410,
        "precio": Decimal("29.90"),
    },
    {
        "titulo": "Bases de datos relacionales",
        "autor": "Marta Ruiz",
        "isbn": ISBN_3,
        "fecha_publicacion": date(2019, 5, 20),
        "paginas": 280,
        "precio": Decimal("18.00"),
    },
    {
        "titulo": "Historia de la informática",
        "autor": "Carlos Vega",
        "isbn": ISBN_4,
        "fecha_publicacion": date(2015, 11, 10),
        "paginas": 240,
        "precio": Decimal("14.75"),
    },
    {
        "titulo": "Cuentos de programadores",
        "autor": "Elena Navarro",
        "isbn": ISBN_5,
        "fecha_publicacion": date(2023, 2, 28),
        "paginas": 150,
        "precio": Decimal("9.95"),
    },
]
for d in datos:
    libro = Libro.objects.create(anio_publicacion=d["fecha_publicacion"].year, **d)
    print(f"Creado: {libro.titulo} ({libro.isbn})")

# 2. READ: recuperar todos los libros y mostrar título y precio con un bucle
print("\n=== 2. Todos los libros ===")
for libro in Libro.objects.all():
    print(f"{libro.titulo}: {libro.precio} €")

# 3. READ: recuperar un libro por su ISBN y mostrar todos sus campos
print("\n=== 3. Libro por ISBN ===")
libro = Libro.objects.get(isbn=ISBN_2)
for campo in libro._meta.fields:
    print(f"{campo.name}: {getattr(libro, campo.name)}")

# 4. UPDATE con instancia y save(): precio y disponibilidad de dos libros
print("\n=== 4. Actualizar con save() ===")
libro = Libro.objects.get(isbn=ISBN_1)
libro.precio = Decimal("24.90")
libro.disponible = False
libro.save()
print(f"{libro.titulo}: {libro.precio} €, disponible={libro.disponible}")

libro = Libro.objects.get(isbn=ISBN_3)
libro.precio = Decimal("15.00")
libro.disponible = False
libro.save()
print(f"{libro.titulo}: {libro.precio} €, disponible={libro.disponible}")

# 5. UPDATE con filter(...).update(...): disponibilidad de otro libro
print("\n=== 5. Actualizar con filter().update() ===")
filas = Libro.objects.filter(isbn=ISBN_4).update(disponible=False)
print(f"Filas actualizadas: {filas}")

# 6. Recuperar un ISBN inexistente y controlar DoesNotExist
print("\n=== 6. ISBN inexistente ===")
try:
    Libro.objects.get(isbn=ISBN_INEXISTENTE)
except Libro.DoesNotExist:
    print(f"No existe ningún libro con ISBN {ISBN_INEXISTENTE}")

# 7. DELETE: eliminar un libro por su ISBN, sin borrar los demás
print("\n=== 7. Eliminar un libro por ISBN ===")
borrados = Libro.objects.get(isbn=ISBN_5).delete()
print(f"Resultado de delete(): {borrados}")

# 8. Comprobación final. Para cumplir el apartado de cerrar y volver a abrir el
# shell, se puede ejecutar después, en una sesión nueva:
#   python manage.py shell -c "from catalogo.models import Libro; print(Libro.objects.count())"
print("\n=== 8. Registros restantes ===")
for libro in Libro.objects.all():
    print(
        f"{libro.isbn} | {libro.titulo} | {libro.precio} € | "
        f"disponible={libro.disponible}"
    )
print(f"Total de libros: {Libro.objects.count()}")
