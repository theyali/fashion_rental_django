import re
import uuid
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name_az = models.CharField(max_length=120, blank=True)
    name_ru = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name_ru"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_az or self.name_ru


class Color(models.Model):
    name_az = models.CharField(max_length=80, blank=True)
    name_ru = models.CharField(max_length=80)
    name_en = models.CharField(max_length=80)
    hex_code = models.CharField(max_length=7, default="#111111")

    class Meta:
        ordering = ["name_ru"]
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name_az or self.name_ru


class Product(models.Model):
    RENTAL = "rental"
    READY = "ready"
    CUSTOM = "custom"
    PRODUCT_TYPES = [(RENTAL, "Аренда"), (READY, "Готовое изделие"), (CUSTOM, "Индивидуальный пошив")]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    slug = models.SlugField(unique=True)
    name_az = models.CharField(max_length=180, blank=True)
    name_ru = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180)
    description_az = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    material_az = models.CharField(max_length=180, blank=True)
    material_ru = models.CharField(max_length=180, blank=True)
    material_en = models.CharField(max_length=180, blank=True)
    composition_az = models.CharField(max_length=220, blank=True)
    composition_ru = models.CharField(max_length=220, blank=True)
    composition_en = models.CharField(max_length=220, blank=True)
    fit_az = models.CharField(max_length=180, blank=True)
    fit_ru = models.CharField(max_length=180, blank=True)
    fit_en = models.CharField(max_length=180, blank=True)
    length_az = models.CharField(max_length=180, blank=True)
    length_ru = models.CharField(max_length=180, blank=True)
    length_en = models.CharField(max_length=180, blank=True)
    care_az = models.CharField(max_length=220, blank=True)
    care_ru = models.CharField(max_length=220, blank=True)
    care_en = models.CharField(max_length=220, blank=True)
    product_type = models.CharField(max_length=12, choices=PRODUCT_TYPES, default=RENTAL)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Цена аренды за 1 календарный день.")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sizes = models.CharField(max_length=120, default="XS, S, M, L")
    colors = models.ManyToManyField(Color, related_name="products", blank=True)
    cover_image = models.ImageField(upload_to="products/covers/", blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-id"]
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

    def __str__(self):
        return self.name_az or self.name_ru

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    GALLERY = "gallery"
    SPIN_360 = "spin360"
    IMAGE_TYPES = [(GALLERY, "Фото галереи"), (SPIN_360, "360° кадр")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_images")
    image = models.ImageField(upload_to="products/media/")
    image_type = models.CharField(max_length=12, choices=IMAGE_TYPES, default=GALLERY)
    angle = models.PositiveSmallIntegerField(default=0, help_text="Для 360°: 0..359")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["image_type", "color_id", "sort_order", "angle", "id"]
        verbose_name = "Фото / 360 кадр"
        verbose_name_plural = "Фото / 360 кадры"

    def __str__(self):
        return f"{self.product} — {self.angle}°" if self.image_type == self.SPIN_360 else f"{self.product} — фото"


class Reservation(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    STATUSES = [(PENDING, "Ожидает подтверждения"), (CONFIRMED, "Подтверждено"), (CANCELLED, "Отменено")]
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reservations")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=30, blank=True)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=12, choices=STATUSES, default=PENDING)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    rental_days = models.PositiveIntegerField(null=True, blank=True, editable=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, editable=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    @property
    def short_code(self):
        return str(self.booking_id).split("-")[0].upper()

    def calculate_pricing(self):
        if self.product_id and self.start_date and self.end_date and self.end_date >= self.start_date and self.product.rental_price is not None:
            self.rental_days = (self.end_date - self.start_date).days + 1
            self.daily_price = self.product.rental_price
            self.total_price = self.daily_price * self.rental_days

    def clean(self):
        errors = {}
        today = timezone.localdate()
        if self.start_date and self.start_date < today:
            errors["start_date"] = "Keçmiş tarix üçün bron yaratmaq olmaz."
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz."
        if self.product_id:
            if self.product.product_type != Product.RENTAL:
                errors["product"] = "Yalnız kirayə məhsullarını bron etmək olar."
            elif self.product.rental_price is None:
                errors["product"] = "Kirayə məhsulu üçün günlük qiymət təyin edilməyib."
            available_sizes = [item.strip() for item in self.product.sizes.split(",") if item.strip()]
            if available_sizes:
                if not self.size:
                    errors["size"] = "Ölçü seçin."
                elif self.size not in available_sizes:
                    errors["size"] = "Seçilmiş ölçü bu məhsul üçün mövcud deyil."
            has_colors = self.product.colors.exists()
            if has_colors and not self.color_id:
                errors["color"] = "Rəng seçin."
            elif self.color_id and not self.product.colors.filter(pk=self.color_id).exists():
                errors["color"] = "Seçilmiş rəng bu məhsula aid deyil."
        if not errors and self.product_id and self.start_date and self.end_date:
            overlap = Reservation.objects.filter(product_id=self.product_id, status__in=[self.PENDING, self.CONFIRMED], start_date__lte=self.end_date, end_date__gte=self.start_date)
            overlap = overlap.filter(color_id=self.color_id) if self.color_id else overlap.filter(color__isnull=True)
            if self.pk:
                overlap = overlap.exclude(pk=self.pk)
            if overlap.exists():
                errors["start_date"] = "Seçilmiş tarixlər artıq bron edilib."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.short_code} · {self.product} / {self.start_date}–{self.end_date}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.name}: {self.email}"


class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=120, default="JALUZINO COUTURE")
    contact_email = models.EmailField(blank=True, default="atelier@example.com")
    contact_phone = models.CharField(max_length=60, blank=True, default="+994 00 000 00 00")
    location_az = models.CharField(max_length=220, blank=True, default="Bakı · öncədən görüşlə")
    location_ru = models.CharField(max_length=220, blank=True, default="Баку · по предварительной записи")
    location_en = models.CharField(max_length=220, blank=True, default="Baku · by appointment")
    whatsapp_phone = models.CharField(max_length=60, blank=True, help_text="Например: +994501234567. Если пусто — WhatsApp-кнопка скрыта.")
    whatsapp_label_az = models.CharField(max_length=100, blank=True, default="İndi bizə yazın")
    whatsapp_label_ru = models.CharField(max_length=100, blank=True, default="Напишите нам")
    whatsapp_label_en = models.CharField(max_length=100, blank=True, default="Ask something now")
    whatsapp_message_az = models.CharField(max_length=240, blank=True, default="Salam! Geyim kirayəsi ilə bağlı sualım var.")
    whatsapp_message_ru = models.CharField(max_length=240, blank=True, default="Здравствуйте! У меня вопрос по аренде одежды.")
    whatsapp_message_en = models.CharField(max_length=240, blank=True, default="Hello! I have a question about a rental.")
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def localized_location(self, lang):
        return {"az": self.location_az or self.location_ru or self.location_en, "ru": self.location_ru or self.location_az or self.location_en, "en": self.location_en or self.location_az or self.location_ru}.get(lang, self.location_az or self.location_ru or self.location_en)

    def localized_whatsapp_label(self, lang):
        return {"az": self.whatsapp_label_az or self.whatsapp_label_en, "ru": self.whatsapp_label_ru or self.whatsapp_label_en, "en": self.whatsapp_label_en or self.whatsapp_label_ru}.get(lang, self.whatsapp_label_en)

    def localized_whatsapp_message(self, lang):
        return {"az": self.whatsapp_message_az or self.whatsapp_message_en, "ru": self.whatsapp_message_ru or self.whatsapp_message_en, "en": self.whatsapp_message_en or self.whatsapp_message_ru}.get(lang, self.whatsapp_message_en)

    def whatsapp_url(self, lang="az"):
        digits = re.sub(r"\D", "", self.whatsapp_phone or "")
        if not digits:
            return ""
        message = quote(self.localized_whatsapp_message(lang) or "")
        return f"https://wa.me/{digits}?text={message}" if message else f"https://wa.me/{digits}"

    def __str__(self):
        return self.brand_name


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_favorite")]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
