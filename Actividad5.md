# Actividad de clase 5

## Actividad 5. Boletín de consultas ORM

**Preparación:** utiliza al menos diez libros con títulos, fechas, precios y disponibilidades variadas. Si tu catálogo tiene menos registros, añade los necesarios mediante el ORM.

Resuelve las siguientes consultas **sin SQL directo**:

1. Mostrar todos los libros.
2. Obtener los libros disponibles.
3. Obtener los libros no disponibles.
4. Buscar libros cuyo título contenga `python`, sin distinguir mayúsculas.
5. Obtener libros con precio superior a 20 euros.
6. Obtener libros con precio entre 10 y 30 euros, ambos incluidos.
7. Obtener libros publicados a partir de 2023.
8. Mostrar libros ordenados alfabéticamente por título.
9. Mostrar libros ordenados por precio descendente.
10. Recuperar los tres libros más baratos.
11. Obtener libros disponibles con más de 250 páginas.
12. Buscar libros cuyo título contenga `python` **o** `django`.
13. Calcular el número total de libros.
14. Calcular el precio medio, máximo y mínimo.
15. Agrupar por disponibilidad e indicar el número de libros de cada grupo.

**Entrega:** archivo `actividad5_consultas.py` con las consultas comentadas y sus resultados, ejecutable mediante `python manage.py shell < actividad5_consultas.py`. No es necesario crear vistas ni plantillas.

**Preguntas:** ¿Por qué `filter()` no falla cuando no encuentra registros? ¿Qué diferencia existe entre `aggregate()` y `annotate()`? ¿Qué devuelve `values()`?

---

## Resolución

### Preparación

Los diez libros se cargan con `cargar_libros.py`. Para partir siempre del mismo estado, se pone `REINICIAR = True` en ese archivo (vacía la tabla de libros y reinicia sus IDs) y se ejecuta:

```bash
python manage.py shell < cargar_libros.py
python manage.py shell < actividad5_consultas.py
```

### Resultados

Con los diez libros de `cargar_libros.py`. La salida completa, libro a libro, la imprime el propio script.

| Consulta                                              | Resultado                                                                                                                        |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1. Todos los libros                                   | 10 libros                                                                                                                        |
| 2. Disponibles                                        | 8 libros                                                                                                                         |
| 3. No disponibles                                     | 2: *Bodas de sangre* y *Programación avanzada con PYTHON*                                                                        |
| 4. Título con `python` (`icontains`)                  | 3: *Aplicaciones web con Django y Python*, *Programación avanzada con PYTHON* y *Python para principiantes*                      |
| 5. Precio superior a 20 €                             | 4 libros                                                                                                                         |
| 6. Precio entre 10 y 30 € (`range`, incluidos)        | 7 libros                                                                                                                         |
| 7. Publicados a partir de 2023                        | 3: *Aplicaciones web con Django y Python*, *Django en la práctica* y *Python para principiantes*                                 |
| 8. Orden alfabético por título                        | De *Aplicaciones web con Django y Python* a *Veinte poemas de amor y una canción desesperada*                                    |
| 9. Precio descendente                                 | De 39,90 € (*Programación avanzada con PYTHON*) a 8,75 € (*Bodas de sangre*)                                                     |
| 10. Tres más baratos                                  | *Bodas de sangre* (8,75 €), *Veinte poemas de amor y una canción desesperada* (9,50 €) e *Historia del software libre* (10,00 €) |
| 11. Disponibles con más de 250 páginas                | 4 libros                                                                                                                         |
| 12. Título con `python` o `django` (`Q` con `\|`)     | 4 libros                                                                                                                         |
| 13. Número total de libros                            | 10                                                                                                                               |
| 14. Precio medio, máximo y mínimo (`aggregate`)       | Media 20,24 €, máximo 39,90 €, mínimo 8,75 €                                                                                     |
| 15. Libros por disponibilidad (`values` + `annotate`) | Disponibles: 8; no disponibles: 2                                                                                                |

## Preguntas

**¿Por qué `filter()` no falla cuando no encuentra registros?**
Porque `filter()` devuelve un `QuerySet`, que representa el conjunto de objetos que cumplen la condición, y un conjunto vacío es un resultado válido (`<QuerySet []>`). Solo `get()` espera exactamente un objeto y lanza `DoesNotExist` si no hay ninguno (o `MultipleObjectsReturned` si hay varios).

**¿Qué diferencia existe entre `aggregate()` y `annotate()`?**
`aggregate()` calcula un valor resumen sobre todo el `QuerySet` y devuelve un diccionario, por ejemplo `{"media": ..., "maximo": ..., "minimo": ...}` (consulta 14). `annotate()` añade un valor calculado a cada elemento del `QuerySet`, o a cada grupo si se usa tras `values()` (consulta 15), y devuelve otro `QuerySet` que se puede seguir encadenando.

**¿Qué devuelve `values()`?**
Un `QuerySet` de diccionarios con solo los campos pedidos, en lugar de objetos `Libro`. Por ejemplo `Libro.objects.values("titulo", "precio")` devuelve `[{'titulo': 'Aplicaciones web con Django y Python', 'precio': Decimal('30.00')}, ...]`. Se utiliza, entre otras cosas, para fijar el criterio de agrupación antes de `annotate()`.

**Siguiente bloque:** relaciones uno a uno, uno a muchos y muchos a muchos.
