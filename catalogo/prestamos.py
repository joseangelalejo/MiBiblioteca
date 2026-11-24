"""Operaciones de préstamo y devolución de libros (Actividad 7, bloque 7).

Cada operación modifica más de un registro, así que se ejecuta dentro de
``transaction.atomic()``: o se guardan todos los cambios o no se guarda ninguno.
"""

from django.db import transaction
from django.utils import timezone

from .models import Libro, Prestamo


def prestar_libro(libro_id, usuario):
    """Registra un préstamo y marca el libro como no disponible."""
    with transaction.atomic():
        # select_for_update() bloquea la fila durante la transacción en gestores
        # compatibles (PostgreSQL). SQLite no bloquea filas.
        libro = Libro.objects.select_for_update().get(pk=libro_id)
        if not libro.disponible:
            raise ValueError("El libro no está disponible")

        prestamo = Prestamo.objects.create(libro=libro, usuario=usuario)
        libro.disponible = False
        libro.save(update_fields=["disponible"])
        return prestamo


def devolver_libro(prestamo_id):
    """Registra la fecha de devolución y vuelve a marcar el libro como disponible."""
    with transaction.atomic():
        prestamo = Prestamo.objects.select_for_update().get(pk=prestamo_id)
        if prestamo.fecha_devolucion is not None:
            raise ValueError("El préstamo ya fue devuelto")

        prestamo.fecha_devolucion = timezone.now()
        prestamo.save(update_fields=["fecha_devolucion"])
        prestamo.libro.disponible = True
        prestamo.libro.save(update_fields=["disponible"])
        return prestamo
