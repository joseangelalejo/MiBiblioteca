# Actividad de clase 3

## 7. Actividad 3. Gestión de migraciones

**Objetivo:** generar, aplicar y comprobar migraciones sobre los modelos del bloque anterior.

1. Ejecutar `makemigrations` y examinar el archivo generado.
2. Ejecutar `migrate` y comprobar que se han creado las tablas.
3. Utilizar `showmigrations` para verificar su estado.
4. Utilizar `sqlmigrate` para examinar las instrucciones SQL.
5. Añadir a `Libro` un campo `recomendado` de tipo booleano con `default=False`.
6. Generar y aplicar la nueva migración.
7. Añadir a `Editorial` un campo `pais` de tipo `CharField`, con longitud máxima y valor predeterminado.
8. Generar y aplicar otra migración.
9. Comprobar en DB Browser for SQLite que aparecen los nuevos campos.

**Entrega:** `models.py`, archivos de migración y capturas de su aplicación.

---

## Resolución

### Migraciones del proyecto

| Migración | Cambio |
| --- | --- |
| `0001_initial` | Crea las tablas de `Autor`, `Editorial` y `Libro` |
| `0002_libro_idioma` | Añade `Libro.idioma` (`default="Español"`), visto en clase |
| `0003_libro_recomendado` | Añade `Libro.recomendado` (`BooleanField`, `default=False`) |
| `0004_editorial_pais` | Añade `Editorial.pais` (`CharField`, `max_length=50`, `default="España"`) |

### Comandos utilizados

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations catalogo
python manage.py sqlmigrate catalogo 0004
```

Estado tras aplicar todo:

```
catalogo
 [X] 0001_initial
 [X] 0002_libro_idioma
 [X] 0003_libro_recomendado
 [X] 0004_editorial_pais
```

`sqlmigrate catalogo 0004` muestra que Django, en SQLite, reconstruye la tabla: crea `new__catalogo_editorial` con el campo nuevo, copia los datos existentes asignando `'España'` a `pais`, elimina la tabla antigua y renombra la nueva. Las editoriales que ya existían antes de migrar quedan, por tanto, con `pais = 'España'`.

## Preguntas de reflexión

**¿Cuál es la diferencia entre generar y aplicar una migración?**
Generar (`makemigrations`) compara los modelos con el estado de las migraciones anteriores y escribe un archivo Python en `catalogo/migrations/` que describe el cambio; no toca la base de datos. Aplicar (`migrate`) ejecuta las migraciones pendientes sobre la base de datos y las registra en la tabla `django_migrations`.

**¿Por qué Django puede pedir un valor predeterminado al añadir un campo obligatorio?**
Porque la tabla puede tener filas ya guardadas y un campo obligatorio no admite `NULL`. Esas filas necesitan un valor al crear la columna, así que Django pregunta cuál usar (o se declara `default` en el campo, como en `idioma`, `recomendado` y `pais`).

**¿Qué información proporciona `showmigrations`?**
Lista, por aplicación, todas las migraciones y su estado: `[X]` si están aplicadas y `[ ]` si están pendientes. Sirve para saber en qué punto está la base de datos respecto al código.

## Resultado esperado

Tablas creadas a partir de los modelos y cambios posteriores aplicados mediante migraciones, sin necesidad de reconstruir la base de datos.
