from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse


class Category(models.Model):
    name_ru = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name_ru"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_ru


class Color(models.Model):
    name_ru = models.CharField(max_length=80)
    name_en = models.CharField(max_length=80)
    hex_code = models.CharField(max_length=7, default="#111111")

    class Meta:
        ordering = ["name_ru"]
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name_ru


class Product(models.Model):
    READY = "ready"
    CUSTOM = "custom"
    PRODUCT_TYPES = [
        (READY, "Готовое изделие / аренда"),
        (CUSTOM, "Индивидуальный пошив"),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    slug = models.SlugField(unique=True)
    name_ru = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    product_type = models.CharField(max_length=12, choices=PRODUCT_TYPES, default=READY)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
        return self.name_ru

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_images")
    image = models.ImageField(upload_to="products/360/")
    angle = models.PositiveSmallIntegerField(default=0, help_text="0..359")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["color_id", "sort_order", "angle"]
        verbose_name = "Фото / 360 кадр"
        verbose_name_plural = "Фото / 360 кадры"

    def __str__(self):
        return f"{self.product} — {self.angle}°"


class Reservation(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    STATUSES = [
        (PENDING, "Ожидает подтверждения"),
        (CONFIRMED, "Подтверждено"),
        (CANCELLED, "Отменено"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reservations")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=12, choices=STATUSES, default=PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")
        if self.product_id and self.start_date and self.end_date:
            overlap = Reservation.objects.filter(
                product_id=self.product_id,
                status__in=[self.PENDING, self.CONFIRMED],
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            if self.pk:
                overlap = overlap.exclude(pk=self.pk)
            if overlap.exists():
                raise ValidationError("Эти даты уже заняты.")

    def __str__(self):
        return f"{self.product} / {self.start_date}–{self.end_date}"


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
