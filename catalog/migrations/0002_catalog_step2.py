from django.db import migrations, models


def move_legacy_ready_products_to_rental(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Product.objects.filter(product_type="ready").update(product_type="rental")


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("rental", "Аренда"),
                    ("ready", "Готовое изделие"),
                    ("custom", "Индивидуальный пошив"),
                ],
                default="rental",
                max_length=12,
            ),
        ),
        migrations.RunPython(
            move_legacy_ready_products_to_rental,
            migrations.RunPython.noop,
        ),
        migrations.AddField(
            model_name="product",
            name="sale_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
