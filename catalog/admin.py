from django.contrib import admin

from .models import Category, Color, ContactMessage, Product, ProductImage, Reservation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image_type", "color", "image", "angle", "sort_order")
    ordering = ("image_type", "color", "sort_order", "angle")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name_az",
        "category",
        "product_type",
        "rental_price",
        "sale_price",
        "custom_price",
        "is_featured",
        "is_active",
    )
    list_filter = ("product_type", "is_featured", "is_active", "category", "colors")
    search_fields = ("name_az", "name_ru", "name_en", "slug")
    prepopulated_fields = {"slug": ("name_en",)}
    filter_horizontal = ("colors",)
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_az", "name_ru", "name_en", "sort_order")
    search_fields = ("name_az", "name_ru", "name_en")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name_az", "name_ru", "name_en", "hex_code")
    search_fields = ("name_az", "name_ru", "name_en")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_type", "color", "angle", "sort_order")
    list_filter = ("image_type", "color", "product")
    search_fields = ("product__name_az", "product__name_ru", "product__name_en")
    list_select_related = ("product", "color")


@admin.action(description="Подтвердить выбранные бронирования")
def confirm_reservations(modeladmin, request, queryset):
    queryset.update(status=Reservation.CONFIRMED)


@admin.action(description="Отменить выбранные бронирования")
def cancel_reservations(modeladmin, request, queryset):
    queryset.update(status=Reservation.CANCELLED)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "short_code_admin",
        "product",
        "color",
        "size",
        "customer_name",
        "start_date",
        "end_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "start_date", "product", "color", "size")
    search_fields = ("customer_name", "email", "phone", "product__name_az", "product__name_ru", "product__name_en")
    list_select_related = ("product", "color")
    date_hierarchy = "start_date"
    actions = [confirm_reservations, cancel_reservations]
    readonly_fields = ("booking_id", "created_at")

    @admin.display(description="Код брони")
    def short_code_admin(self, obj):
        return obj.short_code


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")
