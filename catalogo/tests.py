from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Libro, Prestamo
from .views import devolver_libro, prestar_libro


class PrestamosTests(TestCase):
    """Actividad 7. Se ejecutan con: python manage.py test catalogo

    Django crea una base de datos de prueba aparte, así que no tocan db.sqlite3.
    """

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="lector")
        self.libro = Libro.objects.create(
            titulo="Libro de prueba",
            isbn="9780000009999",
            fecha_publicacion=date(2024, 1, 1),
            anio_publicacion=2024,
            paginas=100,
            precio=Decimal("10.00"),
        )

    def test_prestamo_correcto(self):
        prestamo = prestar_libro(self.libro.pk, self.usuario)
        self.libro.refresh_from_db()
        self.assertFalse(self.libro.disponible)
        self.assertIsNone(prestamo.fecha_devolucion)
        self.assertEqual(self.libro.prestamos.count(), 1)

    def test_prestamo_rechazado_si_no_esta_disponible(self):
        prestar_libro(self.libro.pk, self.usuario)
        with self.assertRaises(ValueError):
            prestar_libro(self.libro.pk, self.usuario)
        self.assertEqual(self.libro.prestamos.count(), 1)

    def test_devolucion_correcta(self):
        prestamo = prestar_libro(self.libro.pk, self.usuario)
        devolver_libro(prestamo.pk)
        prestamo.refresh_from_db()
        self.libro.refresh_from_db()
        self.assertIsNotNone(prestamo.fecha_devolucion)
        self.assertTrue(self.libro.disponible)

    def test_doble_devolucion_rechazada(self):
        prestamo = prestar_libro(self.libro.pk, self.usuario)
        devolver_libro(prestamo.pk)
        with self.assertRaises(ValueError):
            devolver_libro(prestamo.pk)

    def test_rollback(self):
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                self.libro.disponible = False
                self.libro.save(update_fields=["disponible"])
                raise RuntimeError("Error simulado")
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)

    def test_precio_negativo_rechazado_por_la_base_de_datos(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Libro.objects.filter(pk=self.libro.pk).update(precio=-1)

    def test_no_se_borra_un_libro_con_prestamos(self):
        prestar_libro(self.libro.pk, self.usuario)
        with self.assertRaises(ProtectedError):
            self.libro.delete()
