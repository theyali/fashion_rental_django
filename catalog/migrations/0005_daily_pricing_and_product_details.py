from django.db import migrations, models


DETAIL_DEFAULTS = {
    "material_az": "Premium atelye parçası",
    "material_ru": "Премиальная ткань ателье",
    "material_en": "Premium atelier fabric",
    "composition_az": "Dəqiq tərkib məhsul etiketinə uyğun göstərilir",
    "composition_ru": "Точный состав указывается по ярлыку изделия",
    "composition_en": "Exact composition follows the garment label",
    "fit_az": "Siluet və oturuş modeldən asılıdır",
    "fit_ru": "Силуэт и посадка зависят от модели",
    "fit_en": "Silhouette and fit depend on the design",
    "length_az": "Uzunluq modeldən asılıdır və fitting zamanı dəqiqləşdirilir",
    "length_ru": "Длина зависит от модели и уточняется на примерке",
    "length_en": "Length varies by design and is confirmed at fitting",
    "care_az": "Peşəkar quru təmizləmə tövsiyə olunur",
    "care_ru": "Рекомендуется профессиональная химчистка",
    "care_en": "Professional dry cleaning is recommended",
}


def backfill_details_and_prices(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Reservation = apps.get_model("catalog", "Reservation")

    for field, value in DETAIL_DEFAULTS.items():
        Product.objects.filter(**{field: ""}).update(**{field: value})

    reservations = Reservation.objects.select_related("product").all()
    for reservation in reservations.iterator():
        if (
            reservation.start_date
            and reservation.end_date
            and reservation.end_date >= reservation.start_date
            and reservation.product.rental_price is not None
        ):
            days = (reservation.end_date - reservation.start_date).days + 1
            reservation.daily_price = reservation.product.rental_price
            reservation.rental_days = days
            reservation.total_price = reservation.product.rental_price * days
            reservation.save(update_fields=["daily_price", "rental_days", "total_price"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_product_media_step4"),
    ]

    operations = [
        migrations.AddField(model_name="product", name="material_az", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="material_ru", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="material_en", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="composition_az", field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name="product", name="composition_ru", field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name="product", name="composition_en", field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name="product", name="fit_az", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="fit_ru", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="fit_en", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="length_az", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="length_ru", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="length_en", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="product", name="care_az", field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name="product", name="care_ru", field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name="product", name="care_en", field=models.CharField(blank=True, max_length=220)),
        migrations.AlterField(
            model_name="product",
            name="rental_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Цена аренды за 1 календарный день.",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="reservation",
            name="daily_price",
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="reservation",
            name="rental_days",
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="reservation",
            name="total_price",
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=12, null=True),
        ),
        migrations.RunPython(backfill_details_and_prices, migrations.RunPython.noop),
    ]
