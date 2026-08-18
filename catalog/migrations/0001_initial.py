# Generated manually for the starter project.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name_ru", models.CharField(max_length=120)),
                ("name_en", models.CharField(max_length=120)),
                ("slug", models.SlugField(unique=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"verbose_name": "Категория", "verbose_name_plural": "Категории", "ordering": ["sort_order", "name_ru"]},
        ),
        migrations.CreateModel(
            name="Color",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name_ru", models.CharField(max_length=80)),
                ("name_en", models.CharField(max_length=80)),
                ("hex_code", models.CharField(default="#111111", max_length=7)),
            ],
            options={"verbose_name": "Цвет", "verbose_name_plural": "Цвета", "ordering": ["name_ru"]},
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Сообщение", "verbose_name_plural": "Сообщения", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(unique=True)),
                ("name_ru", models.CharField(max_length=180)),
                ("name_en", models.CharField(max_length=180)),
                ("description_ru", models.TextField(blank=True)),
                ("description_en", models.TextField(blank=True)),
                ("product_type", models.CharField(choices=[("ready", "Готовое изделие / аренда"), ("custom", "Индивидуальный пошив")], default="ready", max_length=12)),
                ("rental_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("custom_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("sizes", models.CharField(default="XS, S, M, L", max_length=120)),
                ("cover_image", models.ImageField(blank=True, upload_to="products/covers/")),
                ("is_featured", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.category")),
                ("colors", models.ManyToManyField(blank=True, related_name="products", to="catalog.color")),
            ],
            options={"verbose_name": "Изделие", "verbose_name_plural": "Изделия", "ordering": ["-is_featured", "-id"]},
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="products/360/")),
                ("angle", models.PositiveSmallIntegerField(default=0, help_text="0..359")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("color", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="product_images", to="catalog.color")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="catalog.product")),
            ],
            options={"verbose_name": "Фото / 360 кадр", "verbose_name_plural": "Фото / 360 кадры", "ordering": ["color_id", "sort_order", "angle"]},
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=50)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("status", models.CharField(choices=[("pending", "Ожидает подтверждения"), ("confirmed", "Подтверждено"), ("cancelled", "Отменено")], default="pending", max_length=12)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("color", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="catalog.color")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservations", to="catalog.product")),
            ],
            options={"verbose_name": "Бронирование", "verbose_name_plural": "Бронирования", "ordering": ["-created_at"]},
        ),
    ]
