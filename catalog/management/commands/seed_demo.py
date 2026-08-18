from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from catalog.models import Category, Color, Product, ProductImage


class Command(BaseCommand):
    help = "Create demo categories, products and generated 360 frames"

    PALETTE = {
        "black": (31, 31, 31),
        "burgundy": (111, 29, 46),
        "ivory": (229, 224, 214),
    }

    def handle(self, *args, **options):
        dresses, _ = Category.objects.update_or_create(
            slug="dresses",
            defaults={"name_az": "Donlar", "name_ru": "Платья", "name_en": "Dresses", "sort_order": 1},
        )
        sets, _ = Category.objects.update_or_create(
            slug="sets",
            defaults={"name_az": "Dəstlər", "name_ru": "Комплекты", "name_en": "Sets", "sort_order": 2},
        )

        black, _ = Color.objects.update_or_create(
            name_en="Black",
            defaults={"name_az": "Qara", "name_ru": "Черный", "hex_code": "#1f1f1f"},
        )
        burgundy, _ = Color.objects.update_or_create(
            name_en="Burgundy",
            defaults={"name_az": "Bordo", "name_ru": "Бордовый", "hex_code": "#6f1d2e"},
        )
        ivory, _ = Color.objects.update_or_create(
            name_en="Ivory",
            defaults={"name_az": "Fil sümüyü", "name_ru": "Айвори", "hex_code": "#e5e0d6"},
        )

        p1, _ = Product.objects.update_or_create(
            slug="aurelia-evening-dress",
            defaults={
                "category": dresses,
                "name_az": "Aurelia axşam donu",
                "name_ru": "Вечернее платье Aurelia",
                "name_en": "Aurelia Evening Dress",
                "description_az": "Kirayə üçün zərif axşam donu. Demo kart bron təqvimi, rəng seçimi və 360° baxış imkanını göstərir.",
                "description_ru": "Лаконичное вечернее платье для аренды. Демо-карточка показывает механику календаря, цветов и 360° обзора.",
                "description_en": "A minimal evening rental dress. This demo product shows booking, color selection and the 360° viewer.",
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

        self._ensure_frames(p1, [black, burgundy, ivory])
        self._ensure_frames(p2, [black, burgundy, ivory])
        self._ensure_frames(p3, [black, ivory])
        self._ensure_frames(p4, [ivory, burgundy])
        self.stdout.write(self.style.SUCCESS("Demo catalog is ready."))

    def _ensure_frames(self, product, colors):
        if product.images.exists():
            if not product.cover_image and product.images.first():
                product.cover_image = product.images.first().image.name
                product.save(update_fields=["cover_image"])
            return

        demo_dir = Path(settings.MEDIA_ROOT) / "demo_generated"
        demo_dir.mkdir(parents=True, exist_ok=True)
        first_name = None
        angles = list(range(0, 360, 45))
        for color in colors:
            rgb = self.PALETTE.get(color.name_en.lower(), (40, 40, 40))
            for idx, angle in enumerate(angles):
                path = demo_dir / f"{product.slug}-{color.id}-{angle}.png"
                self._draw_frame(path, rgb, angle, product.product_type)
                with path.open("rb") as fh:
                    obj = ProductImage(product=product, color=color, angle=angle, sort_order=idx)
                    obj.image.save(path.name, File(fh), save=True)
                    if first_name is None:
                        first_name = obj.image.name
        if first_name and not product.cover_image:
            product.cover_image = first_name
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
            points = [
                (cx - shoulder_w // 2, 245),
                (cx + shoulder_w // 2, 245),
                (cx + body_w // 2, 510),
                (cx + hem_w // 2, 900),
                (cx - hem_w // 2, 900),
                (cx - body_w // 2, 510),
            ]
        else:
            points = [
                (cx - shoulder_w // 2, 250),
                (cx + shoulder_w // 2, 250),
                (cx + body_w // 2, 500),
                (cx + hem_w // 2, 850),
                (cx - hem_w // 2, 850),
                (cx - body_w // 2, 500),
            ]
        draw.polygon(points, fill=rgb)
        draw.ellipse((cx - 58, 135, cx + 58, 251), fill=(214, 197, 183))
        draw.line((cx - shoulder_w // 2, 300, cx - body_w, 560), fill=rgb, width=42)
        draw.line((cx + shoulder_w // 2, 300, cx + body_w, 560), fill=rgb, width=42)
        draw.ellipse((cx - 170, 905, cx + 170, 940), fill=(210, 205, 198))
        draw.text((115, 985), f"DEMO 360° / {angle:03d}°", fill=(95, 91, 86))
        image.save(path, quality=92)
