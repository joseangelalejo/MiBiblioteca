from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from unittest import mock

from django.urls import reverse

from .models import Libro, Prestamo
from .prestamos import devolver_libro, prestar_libro


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

    def test_rollback_al_devolver_si_falla_el_segundo_cambio(self):
        """Si falla el segundo cambio, el primero (fecha de devolución) también se revierte."""
        prestamo = prestar_libro(self.libro.pk, self.usuario)
        with mock.patch.object(Libro, "save", side_effect=RuntimeError("Error simulado")):
            with self.assertRaises(RuntimeError):
                devolver_libro(prestamo.pk)
        prestamo.refresh_from_db()
        self.libro.refresh_from_db()
        self.assertIsNone(prestamo.fecha_devolucion)
        self.assertFalse(self.libro.disponible)


class VistasPrestamosTests(TestCase):
    """Las vistas de /prestamo/ y /devolucion/ usan las funciones de prestamos.py."""

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

    def test_prestar_y_devolver(self):
        respuesta = self.client.get(reverse("prestamo", args=[self.libro.pk, self.usuario.pk]))
        self.assertEqual(respuesta.status_code, 200)
        prestamo = Prestamo.objects.get()
        respuesta = self.client.get(reverse("devolucion", args=[prestamo.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)

    def test_libro_no_disponible_devuelve_409(self):
        self.client.get(reverse("prestamo", args=[self.libro.pk, self.usuario.pk]))
        respuesta = self.client.get(reverse("prestamo", args=[self.libro.pk, self.usuario.pk]))
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(Prestamo.objects.count(), 1)

    def test_doble_devolucion_devuelve_409(self):
        self.client.get(reverse("prestamo", args=[self.libro.pk, self.usuario.pk]))
        prestamo = Prestamo.objects.get()
        self.client.get(reverse("devolucion", args=[prestamo.pk]))
        respuesta = self.client.get(reverse("devolucion", args=[prestamo.pk]))
        self.assertEqual(respuesta.status_code, 409)

    def test_ids_inexistentes_devuelven_404(self):
        self.assertEqual(self.client.get(reverse("prestamo", args=[999, self.usuario.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("prestamo", args=[self.libro.pk, 999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("devolucion", args=[999])).status_code, 404)
