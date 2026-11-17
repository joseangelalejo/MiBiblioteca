from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_libros, name="lista_libros"),
    path("libro/<int:pk>/", views.detalle_libro, name="detalle_libro"),
    path("editorial/<int:pk>/", views.editorial, name="editorial"),
    path("autor/<int:pk>/", views.detalle_autor, name="detalle_autor"),
    path("editorial/<int:pk>/libros/", views.lista_editoriales, name="lista_editoriales"),
    path("editorial/<int:pk>/detalle/", views.detalle_editorial, name="detalle_editorial"),
]