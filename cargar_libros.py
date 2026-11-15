from datetime import date
from decimal import Decimal

from django.core.management.color import no_style
from django.db import connection

from catalogo.models import Libro

# Si es True, vacía la tabla de libros y reinicia sus IDs antes de cargar los
# datos. Solo afecta a los libros. Déjalo en False para conservar los actuales.
REINICIAR = False

# Datos de ejemplo. Los ISBN, fechas completas, páginas y precios son ficticios.
libros = [
    {
        "titulo": "Don Quijote de la Mancha",
        "autor": "Miguel de Cervantes",
        "genero": Libro.Genero.NOVELA,
        "anio_publicacion": 1605,
        "disponible": True,
        "isbn": "9780000000011",
        "fecha_publicacion": date(1605, 1, 16),
        "paginas": 1200,
        "precio": Decimal("19.90"),
    },
    {
        "titulo": "Veinte poemas de amor y una canción desesperada",
        "autor": "Pablo Neruda",
        "genero": Libro.Genero.POESIA,
        "anio_publicacion": 1924,
        "disponible": True,
        "isbn": "9780000000028",
        "fecha_publicacion": date(1924, 6, 1),
        "paginas": 96,
        "precio": Decimal("9.50"),
    },
    {
        "titulo": "Bodas de sangre",
        "autor": "Federico García Lorca",
        "genero": Libro.Genero.TEATRO,
        "anio_publicacion": 1933,
        "disponible": False,
        "isbn": "9780000000035",
        "fecha_publicacion": date(1933, 3, 8),
        "paginas": 112,
        "precio": Decimal("8.75"),
    },
    {
        "titulo": "Meditaciones del Quijote",
        "autor": "José Ortega y Gasset",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 1914,
        "disponible": True,
        "isbn": "9780000000042",
        "fecha_publicacion": date(1914, 1, 1),
        "paginas": 180,
        "precio": Decimal("12.00"),
        "dificultad": Libro.Dificultad.AVANZADA,
    },
    {
        "titulo": "Persépolis",
        "autor": "Marjane Satrapi",
        "genero": Libro.Genero.COMIC,
        "anio_publicacion": 2000,
        "disponible": True,
        "isbn": "9780000000059",
        "fecha_publicacion": date(2000, 10, 1),
        "paginas": 160,
        "precio": Decimal("17.50"),
        "dificultad": Libro.Dificultad.INTERMEDIA,
    },
    {
        "titulo": "Python para principiantes",
        "autor": "Laura Gómez",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 2023,
        "disponible": True,
        "isbn": "9780000000066",
        "fecha_publicacion": date(2023, 3, 10),
        "paginas": 320,
        "precio": Decimal("24.95"),
        "dificultad": Libro.Dificultad.BASICA,
    },
    {
        "titulo": "Django en la práctica",
        "autor": "Pedro Ortiz",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 2024,
        "disponible": True,
        "isbn": "9780000000073",
        "fecha_publicacion": date(2024, 6, 5),
        "paginas": 410,
        "precio": Decimal("29.90"),
        "dificultad": Libro.Dificultad.INTERMEDIA,
    },
    {
        "titulo": "Programación avanzada con PYTHON",
        "autor": "Sofía Marín",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 2022,
        "disponible": False,
        "isbn": "9780000000080",
        "fecha_publicacion": date(2022, 11, 18),
        "paginas": 520,
        "precio": Decimal("39.90"),
        "dificultad": Libro.Dificultad.AVANZADA,
    },
    {
        "titulo": "Aplicaciones web con Django y Python",
        "autor": "Raúl Cabrera",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 2025,
        "disponible": True,
        "isbn": "9780000000097",
        "fecha_publicacion": date(2025, 1, 20),
        "paginas": 380,
        "precio": Decimal("30.00"),
        "dificultad": Libro.Dificultad.INTERMEDIA,
    },
    {
        "titulo": "Historia del software libre",
        "autor": "Javier Prieto",
        "genero": Libro.Genero.ENSAYO,
        "anio_publicacion": 2020,
        "disponible": True,
        "isbn": "9780000000103",
        "fecha_publicacion": date(2020, 9, 14),
        "paginas": 210,
        "precio": Decimal("10.00"),
        "dificultad": Libro.Dificultad.BASICA,
    },
]

if REINICIAR:
    # Vacía solo la tabla de libros y reinicia su contador de IDs.
    sql = connection.ops.sql_flush(
        no_style(), [Libro._meta.db_table], reset_sequences=True
    )
    connection.ops.execute_sql_flush(sql)
    print("Tabla de libros reiniciada")

for datos in libros:
    isbn = datos.pop("isbn")
    Libro.objects.get_or_create(isbn=isbn, defaults=datos)

print("Libros en la base de datos:", Libro.objects.count())