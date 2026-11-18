from datetime import date
from decimal import Decimal

from django.core.management.color import no_style
from django.db import connection

from catalogo.models import Autor, Libro

# Si es True, vacía la tabla de libros (y sus relaciones con autores) y reinicia
# sus IDs antes de cargar los datos. No borra los autores ni las editoriales.
# Déjalo en False para conservar los libros actuales.
REINICIAR = False

# Datos de ejemplo. Los ISBN, fechas completas, páginas y precios son ficticios.
# Cada autor se indica como (nombre, apellidos, nacionalidad).
libros = [
    {
        "titulo": "Don Quijote de la Mancha",
        "autores": [("Miguel", "de Cervantes", "Española")],
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
        "autores": [("Pablo", "Neruda", "Chilena")],
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
        "autores": [("Federico", "García Lorca", "Española")],
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
        "autores": [("José", "Ortega y Gasset", "Española")],
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
        "autores": [("Marjane", "Satrapi", "Iraní-francesa")],
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
        "autores": [("Laura", "Gómez", "Desconocida")],
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
        "autores": [("Pedro", "Ortiz", "Desconocida")],
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
        "autores": [("Sofía", "Marín", "Desconocida")],
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
        "autores": [("Raúl", "Cabrera", "Desconocida")],
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
        "autores": [("Javier", "Prieto", "Desconocida")],
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
    # Vacía solo la tabla de libros y la de sus relaciones con autores, y reinicia
    # sus contadores de IDs.
    tablas = [Libro._meta.db_table, Libro.autores.through._meta.db_table]
    sql = connection.ops.sql_flush(no_style(), tablas, reset_sequences=True)
    connection.ops.execute_sql_flush(sql)
    print("Tabla de libros reiniciada")

for datos in libros:
    isbn = datos.pop("isbn")
    autores = datos.pop("autores")
    libro, _ = Libro.objects.get_or_create(isbn=isbn, defaults=datos)
    for nombre, apellidos, nacionalidad in autores:
        autor, _ = Autor.objects.get_or_create(
            nombre=nombre,
            apellidos=apellidos,
            defaults={"nacionalidad": nacionalidad},
        )
        libro.autores.add(autor)

print("Libros en la base de datos:", Libro.objects.count())
print("Autores en la base de datos:", Autor.objects.count())