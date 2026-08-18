from django.contrib import admin
from .models import Category, Color, ContactMessage, Product, ProductImage, Reservation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name_ru",
        "category",
        "product_type",
        "rental_price",
        "sale_price",
        "custom_price",
        "is_featured",
        "is_active",
    )
    list_filter = ("product_type", "is_featured", "is_active", "category", "colors")
    search_fields = ("name_ru", "name_en", "slug")
    prepopulated_fields = {"slug": ("name_en",)}
    filter_horizontal = ("colors",)
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_en", "sort_order")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_en", "hex_code")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("product", "customer_name", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "start_date", "product")
    search_fields = ("customer_name", "email", "phone")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")
