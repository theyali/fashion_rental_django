from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_booking_and_azerbaijani"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimage",
            name="image_type",
            field=models.CharField(
                choices=[("gallery", "Фото галереи"), ("spin360", "360° кадр")],
                default="spin360",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image_type",
            field=models.CharField(
                choices=[("gallery", "Фото галереи"), ("spin360", "360° кадр")],
                default="gallery",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(upload_to="products/media/"),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="angle",
            field=models.PositiveSmallIntegerField(default=0, help_text="Для 360°: 0..359"),
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={
                "ordering": ["image_type", "color_id", "sort_order", "angle", "id"],
                "verbose_name": "Фото / 360 кадр",
                "verbose_name_plural": "Фото / 360 кадры",
            },
        ),
    ]
