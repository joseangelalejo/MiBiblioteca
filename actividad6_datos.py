# pyright: reportAttributeAccessIssue=false
"""Actividad 6. Datos de prueba para las relaciones.

Crea las editoriales y el usuario de prueba, asigna editorial a cinco libros y
añade un segundo autor a uno de ellos. Se puede ejecutar varias veces.
Preparación: tener los diez libros y sus autores en la base de datos
    python manage.py shell < cargar_libros.py
Ejecución:
    python manage.py shell < actividad6_datos.py
"""
from django.contrib.auth import get_user_model

from catalogo.models import Autor, Editorial, Libro, PerfilUsuario

if Libro.objects.count() < 10:
    print("AVISO: faltan libros; ejecuta antes cargar_libros.py")

# 1. Dos editoriales (datos ficticios)
print("\n=== 1. Editoriales ===")
horizonte, _ = Editorial.objects.get_or_create(
    nombre="Editorial Horizonte",
    defaults={
        "email": "contacto@horizonte.example",
        "sitio_web": "https://horizonte.example",
        "pais": "España",
    },
)
del_sur, _ = Editorial.objects.get_or_create(
    nombre="Ediciones del Sur",
    defaults={
        "email": "info@delsur.example",
        "sitio_web": "https://delsur.example",
        "pais": "México",
    },
)
print("Editoriales:", ", ".join(str(e) for e in Editorial.objects.all()))

# 2. Editorial para cinco libros (se identifican por su ISBN)
print("\n=== 2. Editorial de cinco libros ===")
asignaciones = [
    ("9780000000011", horizonte),  # Don Quijote de la Mancha
    ("9780000000028", horizonte),  # Veinte poemas de amor y una canción desesperada
    ("9780000000035", del_sur),    # Bodas de sangre
    ("9780000000042", del_sur),    # Meditaciones del Quijote
    ("9780000000059", horizonte),  # Persépolis
]
for isbn, editorial in asignaciones:
    libro = Libro.objects.get(isbn=isbn)
    libro.editorial = editorial
    libro.save()
    print(f"{libro.titulo} -> {editorial}")

# 3. Un libro con dos autores: se añade un segundo autor a "Django en la práctica"
print("\n=== 3. Libro con dos autores ===")
libro = Libro.objects.get(isbn="9780000000073")
libro.autores.add(Autor.objects.get(nombre="Laura", apellidos="Gómez"))
print(f"{libro.titulo}: {', '.join(str(a) for a in libro.autores.all())}")

# 4. Autores disponibles para las consultas (los crea cargar_libros.py)
print("\n=== 4. Autores ===")
print(f"Autores en la base de datos: {Autor.objects.count()}")

# 5. Usuario de prueba con su perfil (sin contraseña real)
print("\n=== 5. Usuario de prueba con perfil ===")
Usuario = get_user_model()
usuario, creado = Usuario.objects.get_or_create(
    username="lector_prueba", defaults={"email": "lector@example.com"}
)
if creado:
    usuario.set_unusable_password()  # no se puede iniciar sesión con él
    usuario.save()
perfil, _ = PerfilUsuario.objects.get_or_create(
    usuario=usuario, defaults={"biografia": "Usuario de prueba"}
)
print(f"{usuario.username} -> {perfil}")
print(f"Desde el usuario: usuario.perfil = {usuario.perfil}")
