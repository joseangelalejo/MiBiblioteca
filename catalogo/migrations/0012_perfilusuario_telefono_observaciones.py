from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0011_prestamo_y_restriccion_precio"),
    ]

    operations = [
        # biografia pasa a llamarse observaciones (mismo tipo, se conservan los datos)
        migrations.RenameField(
            model_name="perfilusuario",
            old_name="biografia",
            new_name="observaciones",
        ),
        migrations.AddField(
            model_name="perfilusuario",
            name="telefono",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
