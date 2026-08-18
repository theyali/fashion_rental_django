import uuid

from django.db import migrations, models


def populate_booking_ids(apps, schema_editor):
    Reservation = apps.get_model("catalog", "Reservation")
    for reservation in Reservation.objects.filter(booking_id__isnull=True).iterator():
        reservation.booking_id = uuid.uuid4()
        reservation.save(update_fields=["booking_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_catalog_step2"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="name_az",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="color",
            name="name_az",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="product",
            name="description_az",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="name_az",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="reservation",
            name="booking_id",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(populate_booking_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="reservation",
            name="booking_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="reservation",
            name="size",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
