from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    SiteSettings.objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("catalog", "0005_daily_pricing_and_product_details")]
    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand_name", models.CharField(default="JALUZINO COUTURE", max_length=120)),
                ("contact_email", models.EmailField(blank=True, default="atelier@example.com", max_length=254)),
                ("contact_phone", models.CharField(blank=True, default="+994 00 000 00 00", max_length=60)),
                ("location_az", models.CharField(blank=True, default="Bakı · öncədən görüşlə", max_length=220)),
                ("location_ru", models.CharField(blank=True, default="Баку · по предварительной записи", max_length=220)),
                ("location_en", models.CharField(blank=True, default="Baku · by appointment", max_length=220)),
                ("whatsapp_phone", models.CharField(blank=True, help_text="Например: +994501234567. Если пусто — WhatsApp-кнопка скрыта.", max_length=60)),
                ("whatsapp_label_az", models.CharField(blank=True, default="İndi bizə yazın", max_length=100)),
                ("whatsapp_label_ru", models.CharField(blank=True, default="Напишите нам", max_length=100)),
                ("whatsapp_label_en", models.CharField(blank=True, default="Ask something now", max_length=100)),
                ("whatsapp_message_az", models.CharField(blank=True, default="Salam! Geyim kirayəsi ilə bağlı sualım var.", max_length=240)),
                ("whatsapp_message_ru", models.CharField(blank=True, default="Здравствуйте! У меня вопрос по аренде одежды.", max_length=240)),
                ("whatsapp_message_en", models.CharField(blank=True, default="Hello! I have a question about a rental.", max_length=240)),
                ("instagram_url", models.URLField(blank=True)),
                ("facebook_url", models.URLField(blank=True)),
                ("tiktok_url", models.URLField(blank=True)),
                ("youtube_url", models.URLField(blank=True)),
                ("pinterest_url", models.URLField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Настройки сайта", "verbose_name_plural": "Настройки сайта"},
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorites", to="catalog.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorites", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Избранное", "verbose_name_plural": "Избранное", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="favorite", constraint=models.UniqueConstraint(fields=("user", "product"), name="unique_user_product_favorite")),
        migrations.RunPython(create_site_settings, migrations.RunPython.noop),
    ]
