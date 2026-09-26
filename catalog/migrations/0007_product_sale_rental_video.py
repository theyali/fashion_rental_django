from django.db import migrations, models
import django.db.models.deletion


def set_product_flags(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Product.objects.filter(product_type="rental").update(is_rentable=True, is_purchasable=False, min_rental_days=3)
    Product.objects.filter(product_type="ready").update(is_rentable=False, is_purchasable=True, min_rental_days=3)
    Product.objects.filter(product_type="custom").update(is_rentable=False, is_purchasable=False, min_rental_days=3)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_brand_accounts_favorites"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_purchasable",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_rentable",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="product",
            name="min_rental_days",
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.CreateModel(
            name="ProductVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("video", models.FileField(upload_to="products/videos/")),
                ("poster", models.ImageField(blank=True, upload_to="products/video_posters/")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("color", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="product_videos", to="catalog.color")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="videos", to="catalog.product")),
            ],
            options={
                "verbose_name": "Видео изделия",
                "verbose_name_plural": "Видео изделий",
                "ordering": ["color_id", "sort_order", "id"],
            },
        ),
        migrations.RunPython(set_product_flags, migrations.RunPython.noop),
    ]
