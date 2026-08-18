from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from catalog.models import Category, Color, Product, ProductImage


class Command(BaseCommand):
    help = "Create demo catalog, import dresses from /dresses and prepare gallery/360 media"

    PALETTE = {
        "black": (31, 31, 31),
        "burgundy": (111, 29, 46),
        "ivory": (229, 224, 214),
    }

    PRODUCT_DETAILS = {
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

    REAL_DRESSES = [
        {"file": "dress_1.jpeg", "slug": "celeste-evening-dress", "name_az": "Celeste axşam donu", "name_ru": "Вечернее платье Celeste", "name_en": "Celeste Evening Dress", "price": 150, "sizes": "XS, S, M"},
        {"file": "dress_2.jpeg", "slug": "amara-evening-dress", "name_az": "Amara axşam donu", "name_ru": "Вечернее платье Amara", "name_en": "Amara Evening Dress", "price": 170, "sizes": "S, M, L"},
        {"file": "dress_3.jpeg", "slug": "elara-evening-dress", "name_az": "Elara axşam donu", "name_ru": "Вечернее платье Elara", "name_en": "Elara Evening Dress", "price": 180, "sizes": "XS, S, M, L"},
        {"file": "dress_4.jpg", "slug": "noelle-evening-dress", "name_az": "Noelle axşam donu", "name_ru": "Вечернее платье Noelle", "name_en": "Noelle Evening Dress", "price": 200, "sizes": "S, M"},
        {"file": "dress_5.jpeg", "slug": "seraphine-evening-dress", "name_az": "Seraphine axşam donu", "name_ru": "Вечернее платье Seraphine", "name_en": "Seraphine Evening Dress", "price": 165, "sizes": "XS, S, M"},
        {"file": "dress_6.jpeg", "slug": "mirelle-evening-dress", "name_az": "Mirelle axşam donu", "name_ru": "Вечернее платье Mirelle", "name_en": "Mirelle Evening Dress", "price": 145, "sizes": "S, M, L"},
        {"file": "dress_7.avif", "slug": "verona-evening-dress", "name_az": "Verona axşam donu", "name_ru": "Вечернее платье Verona", "name_en": "Verona Evening Dress", "price": 190, "sizes": "XS, S, M, L"},
        {"file": "dress_8.jpg", "slug": "aveline-evening-dress", "name_az": "Aveline axşam donu", "name_ru": "Вечернее платье Aveline", "name_en": "Aveline Evening Dress", "price": 210, "sizes": "S, M"},
        {"file": "dress_9.jpg", "slug": "liora-evening-dress", "name_az": "Liora axşam donu", "name_ru": "Вечернее платье Liora", "name_en": "Liora Evening Dress", "price": 175, "sizes": "XS, S, M"},
        {"file": "dress_10.webp", "slug": "solenne-evening-dress", "name_az": "Solenne axşam donu", "name_ru": "Вечернее платье Solenne", "name_en": "Solenne Evening Dress", "price": 220, "sizes": "S, M, L"},
    ]

    def handle(self, *args, **options):
        dresses, _ = Category.objects.update_or_create(
            slug="dresses",
            defaults={"name_az": "Donlar", "name_ru": "Платья", "name_en": "Dresses", "sort_order": 1},
        )
        sets, _ = Category.objects.update_or_create(
            slug="sets",
            defaults={"name_az": "Dəstlər", "name_ru": "Комплекты", "name_en": "Sets", "sort_order": 2},
        )

        black, _ = Color.objects.update_or_create(name_en="Black", defaults={"name_az": "Qara", "name_ru": "Черный", "hex_code": "#1f1f1f"})
        burgundy, _ = Color.objects.update_or_create(name_en="Burgundy", defaults={"name_az": "Bordo", "name_ru": "Бордовый", "hex_code": "#6f1d2e"})
        ivory, _ = Color.objects.update_or_create(name_en="Ivory", defaults={"name_az": "Fil sümüyü", "name_ru": "Айвори", "hex_code": "#e5e0d6"})
        as_pictured, _ = Color.objects.update_or_create(name_en="As pictured", defaults={"name_az": "Şəkildəki rəng", "name_ru": "Цвет на фото", "hex_code": "#b8afa5"})

        p1, _ = Product.objects.update_or_create(
            slug="aurelia-evening-dress",
            defaults={
                "category": dresses,
                "name_az": "Aurelia axşam donu",
                "name_ru": "Вечернее платье Aurelia",
                "name_en": "Aurelia Evening Dress",
                "description_az": "Kirayə üçün zərif axşam donu. Rəngə görə ayrıca foto qalereyası, bron təqvimi və 360° baxış mövcuddur.",
                "description_ru": "Элегантное вечернее платье для аренды. Доступны отдельные фото по цветам, календарь бронирования и 360° обзор.",
                "description_en": "An elegant evening rental dress with color-specific galleries, booking availability and a 360° viewer.",
                **self.PRODUCT_DETAILS,
                "product_type": Product.RENTAL,
                "rental_price": 180,
                "sale_price": None,
                "custom_price": None,
                "sizes": "XS, S, M, L",
                "is_featured": True,
                "is_active": True,
            },
        )
        p1.colors.set([black, burgundy, ivory])

        p2, _ = Product.objects.update_or_create(
            slug="selene-custom-dress",
            defaults={
                "category": dresses,
                "name_az": "Sifarişlə Selene donu",
                "name_ru": "Платье Selene на заказ",
                "name_en": "Selene Made-to-Order Dress",
                "description_az": "Ölçülərinizə uyğun fərdi tikiş, parça və rəng seçimi ilə.",
                "description_ru": "Индивидуальный пошив по меркам с выбором ткани и цвета.",
                "description_en": "Made to measure with fabric and color selection.",
                **self.PRODUCT_DETAILS,
                "product_type": Product.CUSTOM,
                "rental_price": None,
                "sale_price": None,
                "custom_price": 950,
                "sizes": "Fərdi ölçü",
                "is_featured": True,
                "is_active": True,
            },
        )
        p2.colors.set([black, burgundy, ivory])

        p3, _ = Product.objects.update_or_create(
            slug="noir-tailored-set",
            defaults={
                "category": sets,
                "name_az": "Noir dəsti",
                "name_ru": "Комплект Noir",
                "name_en": "Noir Tailored Set",
                "description_az": "Tədbir, şam yeməyi və ya çəkiliş üçün kirayəyə hazır dəst.",
                "description_ru": "Готовый комплект для аренды на событие, ужин или съемку.",
                "description_en": "A ready tailored set available for event, dinner or editorial rental.",
                **self.PRODUCT_DETAILS,
                "product_type": Product.RENTAL,
                "rental_price": 140,
                "sale_price": None,
                "custom_price": None,
                "sizes": "S, M, L",
                "is_featured": False,
                "is_active": True,
            },
        )
        p3.colors.set([black, ivory])

        p4, _ = Product.objects.update_or_create(
            slug="ivory-sculpted-dress",
            defaults={
                "category": dresses,
                "name_az": "Ivory heykəltəraş formalı don",
                "name_ru": "Скульптурное платье Ivory",
                "name_en": "Ivory Sculpted Dress",
                "description_az": "Cari kolleksiyadan artıq tikilmiş don. Fittingdən sonra almaq mümkündür.",
                "description_ru": "Уже сшитое платье из текущей коллекции. Доступно для покупки после примерки.",
                "description_en": "A finished piece from the current collection, available to purchase after fitting.",
                **self.PRODUCT_DETAILS,
                "product_type": Product.READY,
                "rental_price": None,
                "sale_price": 720,
                "custom_price": None,
                "sizes": "S, M",
                "is_featured": True,
                "is_active": True,
            },
        )
        p4.colors.set([ivory, burgundy])

        self._ensure_demo_media(p1, [black, burgundy, ivory])
        self._ensure_demo_media(p2, [black, burgundy, ivory])
        self._ensure_demo_media(p3, [black, ivory])
        self._ensure_demo_media(p4, [ivory, burgundy])
        self._import_real_dresses(dresses, as_pictured)

        self.stdout.write(self.style.SUCCESS("Catalog, dress details and daily pricing are ready."))

    def _import_real_dresses(self, category, color):
        source_dir = Path(settings.BASE_DIR) / "dresses"
        if not source_dir.exists():
            self.stdout.write(self.style.WARNING("/dresses folder was not found; real dress import skipped."))
            return

        description_az = "Atelye kolleksiyasından seçilmiş don. Tədbir və çəkiliş üçün günlük kirayəyə verilir; rəng, ölçü və boş tarixlər məhsul səhifəsində seçilir."
        description_ru = "Платье из коллекции ателье для посуточной аренды на событие или съемку. Цвет, размер и свободные даты выбираются в карточке изделия."
        description_en = "A selected atelier dress available for daily event or editorial rental. Choose the color, size and available dates on the product page."

        for index, item in enumerate(self.REAL_DRESSES):
            product, _ = Product.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": category,
                    "name_az": item["name_az"],
                    "name_ru": item["name_ru"],
                    "name_en": item["name_en"],
                    "description_az": description_az,
                    "description_ru": description_ru,
                    "description_en": description_en,
                    **self.PRODUCT_DETAILS,
                    "product_type": Product.RENTAL,
                    "rental_price": item["price"],
                    "sale_price": None,
                    "custom_price": None,
                    "sizes": item["sizes"],
                    "is_featured": index < 4,
                    "is_active": True,
                },
            )
            product.colors.set([color])
            self._import_gallery_photo(product, color, source_dir / item["file"])

    def _import_gallery_photo(self, product, color, source_path):
        photo = product.images.filter(image_type=ProductImage.GALLERY, color=color, sort_order=0).first()
        if not photo:
            if not source_path.exists():
                self.stdout.write(self.style.WARNING(f"Missing dress image: {source_path.name}"))
                return
            with source_path.open("rb") as fh:
                photo = ProductImage(product=product, color=color, image_type=ProductImage.GALLERY, angle=0, sort_order=0)
                photo.image.save(f"{product.slug}{source_path.suffix.lower()}", File(fh), save=True)

        if photo and product.cover_image.name != photo.image.name:
            product.cover_image = photo.image.name
            product.save(update_fields=["cover_image"])

    def _ensure_demo_media(self, product, colors):
        demo_dir = Path(settings.MEDIA_ROOT) / "demo_generated"
        demo_dir.mkdir(parents=True, exist_ok=True)
        angles = list(range(0, 360, 45))
        first_cover = None

        for color in colors:
            frames = product.images.filter(color=color, image_type=ProductImage.SPIN_360).order_by("angle", "sort_order")
            if not frames.exists():
                rgb = self.PALETTE.get(color.name_en.lower(), (40, 40, 40))
                for idx, angle in enumerate(angles):
                    path = demo_dir / f"{product.slug}-{color.id}-{angle}.png"
                    self._draw_frame(path, rgb, angle, product.product_type)
                    with path.open("rb") as fh:
                        frame = ProductImage(product=product, color=color, image_type=ProductImage.SPIN_360, angle=angle, sort_order=idx)
                        frame.image.save(path.name, File(fh), save=True)
                frames = product.images.filter(color=color, image_type=ProductImage.SPIN_360).order_by("angle", "sort_order")

            first_frame = frames.first()
            gallery_photo = product.images.filter(color=color, image_type=ProductImage.GALLERY).order_by("sort_order", "id").first()
            if not gallery_photo and first_frame:
                gallery_photo = ProductImage.objects.create(product=product, color=color, image=first_frame.image.name, image_type=ProductImage.GALLERY, angle=0, sort_order=0)
            if first_cover is None and gallery_photo:
                first_cover = gallery_photo.image.name

        if first_cover and product.cover_image.name != first_cover:
            product.cover_image = first_cover
            product.save(update_fields=["cover_image"])

    def _draw_frame(self, path, rgb, angle, product_type):
        width, height = 900, 1100
        image = Image.new("RGB", (width, height), (242, 239, 234))
        draw = ImageDraw.Draw(image)
        draw.rectangle((95, 70, 805, 1030), fill=(235, 231, 225))
        cx = width // 2
        yaw = abs(((angle + 90) % 180) - 90) / 90
        body_w = int(250 - yaw * 70)
        shoulder_w = int(body_w * 0.85)
        hem_w = int(body_w * 1.55)

        if product_type == Product.CUSTOM:
            points = [(cx - shoulder_w // 2, 245), (cx + shoulder_w // 2, 245), (cx + body_w // 2, 510), (cx + hem_w // 2, 900), (cx - hem_w // 2, 900), (cx - body_w // 2, 510)]
        else:
            points = [(cx - shoulder_w // 2, 250), (cx + shoulder_w // 2, 250), (cx + body_w // 2, 500), (cx + hem_w // 2, 850), (cx - hem_w // 2, 850), (cx - body_w // 2, 500)]
        draw.polygon(points, fill=rgb)
        draw.ellipse((cx - 58, 135, cx + 58, 251), fill=(214, 197, 183))
        draw.line((cx - shoulder_w // 2, 300, cx - body_w, 560), fill=rgb, width=42)
        draw.line((cx + shoulder_w // 2, 300, cx + body_w, 560), fill=rgb, width=42)
        draw.ellipse((cx - 170, 905, cx + 170, 940), fill=(210, 205, 198))
        draw.text((115, 985), f"DEMO 360° / {angle:03d}°", fill=(95, 91, 86))
        image.save(path, quality=92)
