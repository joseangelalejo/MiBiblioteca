from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from unittest import mock

from django.urls import reverse

from .models import Libro, Prestamo
from .views import (
    devolver_libro,
    buscar_libros,
    crear_editorial_y_autores,
    crear_tres_libros,
    eliminar_libro,
    libro_por_isbn,
    libros_de_autor,
    libros_de_editorial,
    libros_disponibles,
    libros_por_editorial,
    modificar_precio,
    precio_medio,
    prestamos_activos,
    prestar_libro,
)


class PrestamosTests(TestCase):
    """Se ejecutan con: python manage.py test catalogo

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
    """Las vistas de /prestamo/ y /devolucion/ llaman a prestar_libro y devolver_libro."""

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

class IntegradoraTests(TestCase):
    """Restricción de préstamo activo, CRUD, consultas y panel de administración."""

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="lector_integradora")
        self.editorial, self.autor_uno, self.autor_dos = crear_editorial_y_autores()
        self.libros = crear_tres_libros(self.editorial, self.autor_uno, self.autor_dos)

    def test_un_solo_prestamo_activo_por_libro(self):
        libro = self.libros[0]
        Prestamo.objects.create(libro=libro, usuario=self.usuario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Prestamo.objects.create(libro=libro, usuario=self.usuario)

    def test_se_puede_prestar_de_nuevo_tras_la_devolucion(self):
        libro = self.libros[0]
        prestamo = prestar_libro(libro.pk, self.usuario)
        devolver_libro(prestamo.pk)
        self.assertIsNotNone(prestar_libro(libro.pk, self.usuario))

    def test_crud(self):
        self.assertEqual(Libro.objects.filter(editorial=self.editorial).count(), 3)
        self.assertEqual(self.libros[1].autores.count(), 2)
        libro = libro_por_isbn("9780000001001")
        self.assertEqual(libro.titulo, "Libro Demo 1")
        self.assertEqual(modificar_precio("9780000001001", Decimal("15.00")).precio, Decimal("15.00"))
        eliminar_libro("9780000001003")
        self.assertFalse(Libro.objects.filter(isbn="9780000001003").exists())

    def test_no_se_elimina_un_libro_con_prestamos(self):
        prestar_libro(self.libros[0].pk, self.usuario)
        with self.assertRaises(ValueError):
            eliminar_libro("9780000001001")

    def test_consultas(self):
        prestar_libro(self.libros[0].pk, self.usuario)
        self.assertEqual(
            [libro.titulo for libro in libros_disponibles()], ["Libro Demo 2", "Libro Demo 3"]
        )
        self.assertEqual(buscar_libros("demo 2").count(), 1)
        self.assertEqual(libros_de_editorial(self.editorial.pk).count(), 3)
        self.assertEqual(libros_de_autor(self.autor_dos.pk).count(), 2)
        self.assertEqual(round(precio_medio(), 2), Decimal("13.47"))  # (12,50 + 18,00 + 9,90) / 3
        self.assertEqual(libros_por_editorial().get(pk=self.editorial.pk).total_libros, 3)
        self.assertEqual([p.libro.isbn for p in prestamos_activos()], ["9780000001001"])

    def test_panel_de_administracion(self):
        admin_user = get_user_model().objects.create_superuser(username="admin_integradora")
        self.client.force_login(admin_user)
        for modelo in ("libro", "autor", "editorial", "perfilusuario", "prestamo"):
            url = reverse(f"admin:catalogo_{modelo}_changelist")
            self.assertEqual(self.client.get(url).status_code, 200, modelo)
            self.assertEqual(self.client.get(reverse(f"admin:catalogo_{modelo}_add")).status_code, 200, modelo)
        url = reverse("admin:catalogo_libro_changelist")
        self.assertEqual(self.client.get(url, {"q": "9780000001001"}).status_code, 200)
        self.assertEqual(self.client.get(url, {"editorial__id__exact": self.editorial.pk}).status_code, 200)
        self.assertEqual(self.client.get(url, {"disponible__exact": "1"}).status_code, 200)
