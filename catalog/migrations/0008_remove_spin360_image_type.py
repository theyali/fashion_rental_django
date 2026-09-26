from django.db import migrations, models


def delete_spin360_images(apps, schema_editor):
    ProductImage = apps.get_model("catalog", "ProductImage")
    ProductImage.objects.filter(image_type="spin360").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_product_sale_rental_video"),
    ]

    operations = [
        migrations.RunPython(delete_spin360_images, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="productimage",
            name="angle",
            field=models.PositiveSmallIntegerField(default=0, help_text="Не используется для обычной галереи."),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image_type",
            field=models.CharField(choices=[("gallery", "Фото галереи")], default="gallery", max_length=12),
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={"ordering": ["image_type", "color_id", "sort_order", "angle", "id"], "verbose_name": "Фото изделия", "verbose_name_plural": "Фото изделий"},
        ),
    ]
