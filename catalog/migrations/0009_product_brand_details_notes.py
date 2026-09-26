from django.db import migrations, models


def fill_product_details(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    defaults = {
        "brand": "JALUZINO COUTURE",
        "extra_details_az": "Fitting zamanı ölçü, kirayə müddəti və aksesuar uyğunluğu birlikdə dəqiqləşdirilir.",
        "extra_details_ru": "На примерке уточняются размер, срок аренды и сочетание с аксессуарами.",
        "extra_details_en": "Sizing, rental duration and accessory pairing are confirmed at fitting.",
        "additional_note_az": "Bron sorğusunda tədbir tarixini və istədiyiniz fitting vaxtını qeyd edə bilərsiniz.",
        "additional_note_ru": "В заявке можно указать дату события и желаемое время примерки.",
        "additional_note_en": "You can note the event date and preferred fitting time in the booking request.",
    }
    for field, value in defaults.items():
        Product.objects.filter(**{field: ""}).update(**{field: value})


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_remove_spin360_image_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="additional_note_az",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="additional_note_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="additional_note_ru",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.CharField(blank=True, default="JALUZINO COUTURE", max_length=160),
        ),
        migrations.AddField(
            model_name="product",
            name="extra_details_az",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="extra_details_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="extra_details_ru",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(fill_product_details, migrations.RunPython.noop),
    ]
