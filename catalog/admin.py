from django.contrib import admin

from .models import Category, Color, ContactMessage, Favorite, Product, ProductImage, Reservation, SiteSettings


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image_type", "color", "image", "angle", "sort_order")
    ordering = ("image_type", "color", "sort_order", "angle")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_az", "category", "product_type", "rental_price", "sale_price", "custom_price", "is_featured", "is_active")
    list_filter = ("product_type", "is_featured", "is_active", "category", "colors")
    search_fields = ("name_az", "name_ru", "name_en", "slug")
    prepopulated_fields = {"slug": ("name_en",)}
    filter_horizontal = ("colors",)
    inlines = [ProductImageInline]
    fieldsets = (
        ("Основное", {"fields": ("category", "slug", "product_type", "sizes", "colors", "cover_image", "is_featured", "is_active")}),
        ("AZ", {"fields": ("name_az", "description_az", "material_az", "composition_az", "fit_az", "length_az", "care_az")}),
        ("RU", {"fields": ("name_ru", "description_ru", "material_ru", "composition_ru", "fit_ru", "length_ru", "care_ru")}),
        ("EN", {"fields": ("name_en", "description_en", "material_en", "composition_en", "fit_en", "length_en", "care_en")}),
        ("Цены", {"fields": ("rental_price", "sale_price", "custom_price"), "description": "Для аренды rental_price — цена за один календарный день."}),
    )


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
    list_display = ("short_code_admin", "product", "color", "size", "customer_name", "start_date", "end_date", "rental_days", "daily_price", "total_price", "status", "created_at")
    list_filter = ("status", "start_date", "product", "color", "size")
    search_fields = ("customer_name", "email", "phone", "product__name_az", "product__name_ru", "product__name_en")
    list_select_related = ("product", "color")
    date_hierarchy = "start_date"
    actions = [confirm_reservations, cancel_reservations]
    readonly_fields = ("booking_id", "daily_price", "rental_days", "total_price", "created_at")

    def save_model(self, request, obj, form, change):
        if not change or {"product", "start_date", "end_date"} & set(form.changed_data):
            obj.calculate_pricing()
        super().save_model(request, obj, form, change)

    @admin.display(description="Код брони")
    def short_code_admin(self, obj):
        return obj.short_code


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Бренд", {"fields": ("brand_name",)}),
        ("Контакты", {"fields": ("contact_email", "contact_phone", "location_az", "location_ru", "location_en")}),
        ("WhatsApp", {"fields": ("whatsapp_phone", "whatsapp_label_az", "whatsapp_label_ru", "whatsapp_label_en", "whatsapp_message_az", "whatsapp_message_ru", "whatsapp_message_en")}),
        ("Социальные сети", {"fields": ("instagram_url", "facebook_url", "tiktok_url", "youtube_url", "pinterest_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at", "product")
    search_fields = ("user__username", "user__email", "product__name_az", "product__name_ru", "product__name_en")
    list_select_related = ("user", "product")
