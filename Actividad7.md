# Actividad de clase 7

## Actividad 7. Préstamos e integridad

**Enunciado:** Amplía la biblioteca para gestionar préstamos con operaciones consistentes.

1. Añade el modelo `Prestamo` y aplica las migraciones.
2. Incorpora una restricción que impida precios negativos en `Libro`.
3. Implementa `prestar_libro(libro_id, usuario)` con `transaction.atomic()`.
4. Impide prestar un libro marcado como no disponible.
5. Implementa `devolver_libro(prestamo_id)` para registrar la fecha de devolución y volver a marcar el libro como disponible.
6. Impide devolver dos veces el mismo préstamo.
7. Simula un error dentro de una transacción y comprueba que el cambio se revierte.
8. Explica por qué `select_for_update()` no proporciona bloqueo de filas en SQLite y qué cambia al utilizar PostgreSQL.

**Entrega:** modelos y migraciones, archivo con las funciones de préstamo/devolución, y pruebas de un préstamo correcto, una operación rechazada y un rollback.

---

## Resolución

### Archivos

| Archivo                                                     | Contenido                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `catalogo/models.py`                                        | `Prestamo` y `CheckConstraint` de `Libro.precio` en `Meta.constraints`       |
| `catalogo/migrations/0011_prestamo_y_restriccion_precio.py` | Crea `Prestamo` y la restricción `libro_precio_no_negativo`                  |
| `catalogo/prestamos.py`                                     | Funciones `prestar_libro(libro_id, usuario)` y `devolver_libro(prestamo_id)` |
| `catalogo/views.py`, `catalogo/urls.py`                     | Vistas `prestar_libro` y `devolver_libro` con sus rutas (visto en clase)     |
| `catalogo/tests.py`                                         | Pruebas de préstamo correcto, operación rechazada y rollback                 |

### 1. Modelo `Prestamo` y migración

```python
class Prestamo(models.Model):
    libro = models.ForeignKey("Libro", on_delete=models.PROTECT, related_name="prestamos")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prestamos_biblioteca"
    )
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
```

- `fecha_prestamo` se rellena sola al crear el préstamo (`auto_now_add=True`).
- `fecha_devolucion` es nula mientras el préstamo siga activo.
- `PROTECT` en las dos claves impide borrar un libro o un usuario con préstamos.

```bash
python manage.py makemigrations catalogo
python manage.py migrate
```

### 2. Restricción de precio

```python
class Meta:
    ordering = ["titulo"]
    constraints = [
        models.CheckConstraint(
            condition=models.Q(precio__gte=0),
            name="libro_precio_no_negativo",
        ),
    ]
```

La comprobación la hace la base de datos. Un `Libro.objects.create(..., precio=-1)` lanza `IntegrityError`.

### 3 a 6. Préstamo y devolución con `transaction.atomic()`

```python
def prestar_libro(libro_id, usuario):
    with transaction.atomic():
        libro = Libro.objects.select_for_update().get(pk=libro_id)
        if not libro.disponible:
            raise ValueError("El libro no está disponible")

        prestamo = Prestamo.objects.create(libro=libro, usuario=usuario)
        libro.disponible = False
        libro.save(update_fields=["disponible"])
        return prestamo


def devolver_libro(prestamo_id):
    with transaction.atomic():
        prestamo = Prestamo.objects.select_for_update().get(pk=prestamo_id)
        if prestamo.fecha_devolucion is not None:
            raise ValueError("El préstamo ya fue devuelto")

        prestamo.fecha_devolucion = timezone.now()
        prestamo.save(update_fields=["fecha_devolucion"])
        prestamo.libro.disponible = True
        prestamo.libro.save(update_fields=["disponible"])
        return prestamo
```

- Prestar y devolver cambian **dos registros** cada una, por eso van dentro de una transacción: se guardan los dos cambios o ninguno.
- Un libro no disponible se rechaza con `ValueError`, y un préstamo ya devuelto también.
- El préstamo no se borra al devolver: se conserva como histórico y solo se rellena `fecha_devolucion`.

**Vistas y rutas (clase del 24/11).** Las vistas llaman a estas funciones y devuelven un `HttpResponse` sencillo. Si la operación se rechaza responden con `409`, y con `404` si el libro, el usuario o el préstamo no existen.

| Ruta                                 | Acción                              |
| ------------------------------------ | ----------------------------------- |
| `/prestamo/<id libro>/<id usuario>/` | Presta el libro al usuario          |
| `/devolucion/<id préstamo>/`         | Registra la devolución del préstamo |

### 7. Rollback simulado

```python
from django.db import transaction
from catalogo.models import Libro

libro = Libro.objects.filter(disponible=True).first()
try:
    with transaction.atomic():
        libro.disponible = False
        libro.save(update_fields=["disponible"])
        raise RuntimeError("Error simulado")
except RuntimeError:
    pass

libro.refresh_from_db()
print(libro.disponible)  # True: el cambio se revirtió
```

El error se captura **fuera** del bloque `atomic()`. Si se capturase dentro, la transacción no se enteraría del fallo y confirmaría los cambios.

### Pruebas

```bash
python manage.py test catalogo
```

| Prueba                                                 | Qué comprueba                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `test_prestamo_correcto`                               | Se crea el préstamo y el libro queda no disponible                             |
| `test_prestamo_rechazado_si_no_esta_disponible`        | El segundo préstamo del mismo libro lanza `ValueError` y no crea otro préstamo |
| `test_devolucion_correcta`                             | Se rellena `fecha_devolucion` y el libro vuelve a estar disponible             |
| `test_doble_devolucion_rechazada`                      | Devolver dos veces el mismo préstamo lanza `ValueError`                        |
| `test_rollback`                                        | Un error dentro de `atomic()` revierte el cambio del libro                     |
| `test_rollback_al_devolver_si_falla_el_segundo_cambio` | Si falla el cambio del libro, la fecha de devolución también se revierte       |
| `test_precio_negativo_rechazado_por_la_base_de_datos`  | `precio=-1` lanza `IntegrityError`                                             |
| `test_no_se_borra_un_libro_con_prestamos`              | `PROTECT` lanza `ProtectedError`                                               |
| `VistasPrestamosTests`                                 | Las rutas responden `200`, `409` o `404` según el caso                         |

### 8. `select_for_update()` en SQLite y en PostgreSQL

`select_for_update()` añade `FOR UPDATE` a la consulta: la fila se bloquea hasta que termina la transacción y otra transacción que intente bloquearla espera. **SQLite no admite ese bloqueo de filas**: Django ignora `select_for_update()` y la consulta se ejecuta como un `get()` normal. En SQLite la transacción atómica sí funciona (el rollback se comprueba en las pruebas), pero no protege frente a dos usuarios que prestan el mismo libro a la vez. Con PostgreSQL la segunda transacción espera a que termine la primera, ve entonces `disponible = False` y se rechaza.

## Preguntas de reflexión

**¿Por qué no basta con cambiar `disponible` sin crear el préstamo?**
Porque el libro quedaría marcado como prestado sin saber a quién, desde cuándo ni cuándo se devolvió, y no habría préstamo que cerrar al devolverlo. Además se perdería el histórico.

**¿Qué diferencia existe entre validación de Django y restricción de base de datos?**
La validación de Django (`blank=False`, validadores, `full_clean()`) se ejecuta en Python, por ejemplo al validar un formulario, y `save()` no la llama sola. La restricción de base de datos (`unique`, `CheckConstraint`, claves foráneas) la aplica el gestor en cualquier escritura, también con `update()` o desde un script.

**¿Qué ocurre si una excepción sale del bloque `atomic()`?**
Se revierten todos los cambios hechos dentro del bloque y la excepción se propaga a quien llamó a la función.

## Resultado esperado

Préstamos y devoluciones que modifican varios registros de forma atómica, con las reglas de integridad en la base de datos y un rollback comprobado.
