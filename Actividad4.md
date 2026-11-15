# Actividad de clase 4

## Actividad 4. Gestión CRUD del catálogo

**Enunciado:** A partir del proyecto `biblioteca`, realiza las siguientes operaciones exclusivamente con el ORM desde Django Shell.

1. Crea **cinco libros** con ISBN distintos, título, fecha de publicación, páginas y precio.
2. Recupera todos los libros y muestra su título y precio mediante un bucle.
3. Recupera un libro por su ISBN y muestra todos sus campos.
4. Cambia el precio y la disponibilidad de dos libros usando instancias y `save()`.
5. Actualiza la disponibilidad de otro libro con `filter(...).update(...)`.
6. Intenta recuperar un ISBN inexistente y controla `DoesNotExist`.
7. Elimina un libro identificado por su ISBN, sin borrar los demás.
8. Cierra el shell, ábrelo de nuevo y comprueba los registros restantes.

**Entrega:** archivo `actividad4_crud.py` con las instrucciones ejecutadas (o transcripción ordenada del shell) y capturas de la consulta final. Si se utiliza un script, ejecútalo dentro del contexto de Django, por ejemplo con `python manage.py shell < actividad4_crud.py`.

**Preguntas:** ¿Qué diferencia hay entre `create()` y `save()`? ¿Qué ocurre al usar `get()` con un ISBN inexistente? ¿Qué riesgo tiene ejecutar `all().delete()`?

---

## Resolución

El script `actividad4_crud.py` realiza los ocho apartados en orden y se ejecuta con:

```bash
python manage.py shell < actividad4_crud.py
```

Antes de crear los libros borra únicamente los cinco de esta actividad (por ISBN), de modo que el script se puede repetir sin errores de ISBN duplicado y sin tocar ningún otro libro.

Para el apartado 8 (cerrar el shell y abrirlo de nuevo), en una sesión nueva:

```bash
python manage.py shell -c "from catalogo.models import Libro; print(Libro.objects.count())"
```

### Salida de la ejecución

Obtenida sobre una base de datos nueva. Si hay más libros cargados, aparecerán también en los apartados 2 y 8.

```bash
=== 1. Crear cinco libros ===
Creado: Python para todos (9780000001001)
Creado: Django desde cero (9780000001002)
Creado: Bases de datos relacionales (9780000001003)
Creado: Historia de la informática (9780000001004)
Creado: Cuentos de programadores (9780000001005)

=== 2. Todos los libros ===
Bases de datos relacionales: 18.00 €
Cuentos de programadores: 9.95 €
Django desde cero: 29.90 €
Historia de la informática: 14.75 €
Python para todos: 22.50 €

=== 3. Libro por ISBN ===
id: 2
titulo: Django desde cero
autor: Luis Herrera
isbn: 9780000001002
sinopsis: 
fecha_publicacion: 2022-09-01
anio_publicacion: 2022
paginas: 410
precio: 29.90
disponible: True
recomendado: False
idioma: Español
genero: NOV
dificultad: 1

=== 4. Actualizar con save() ===
Python para todos: 24.90 €, disponible=False
Bases de datos relacionales: 15.00 €, disponible=False

=== 5. Actualizar con filter().update() ===
Filas actualizadas: 1

=== 6. ISBN inexistente ===
No existe ningún libro con ISBN 9780000009999

=== 7. Eliminar un libro por ISBN ===
Resultado de delete(): (1, {'catalogo.Libro': 1})

=== 8. Registros restantes ===
9780000001003 | Bases de datos relacionales | 15.00 € | disponible=False
9780000001002 | Django desde cero | 29.90 € | disponible=True
9780000001004 | Historia de la informática | 14.75 € | disponible=False
9780000001001 | Python para todos | 24.90 € | disponible=False
Total de libros: 4
```

## Preguntas

**¿Qué diferencia hay entre `create()` y `save()`?**
`create()` construye el objeto y lo guarda en la base de datos en una sola llamada (un `INSERT`) y devuelve la instancia. `save()` se llama sobre una instancia ya creada en memoria: hace un `INSERT` si el objeto es nuevo y un `UPDATE` si ya existe en la base de datos, lo que permite modificar atributos antes de guardar.

**¿Qué ocurre al usar `get()` con un ISBN inexistente?**
Lanza la excepción `Libro.DoesNotExist` en lugar de devolver `None` o una lista vacía, por eso se captura con `try/except`. Si encontrara más de un registro lanzaría `MultipleObjectsReturned`; con el ISBN único no puede ocurrir.

**¿Qué riesgo tiene ejecutar `all().delete()`?**
Elimina de golpe todos los registros del modelo, sin pedir confirmación y de forma irreversible salvo que haya copia de seguridad. Si existen relaciones, el borrado puede propagarse en cascada a los objetos relacionados. Por eso conviene acotar siempre con `filter()` o `get()`.

**Siguiente bloque:** consultas ORM, filtrado, ordenación y agregaciones.
