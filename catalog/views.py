import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import connection, transaction
from django.db.models import Case, DecimalField, F, When
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ContactForm, ReservationForm
from .models import Category, Color, Product, ProductImage, Reservation


SUPPORTED_LANGUAGES = {"az", "ru", "en"}

SEO_COPY = {
    "az": {
        "home": ("Atelier Rental — Bakıda geyim kirayəsi", "Bakıda dizayner geyimlərinin kirayəsi, hazır kolleksiya və fərdi tikiş. Onlayn bron, rəng seçimi və 360° baxış."),
        "catalog": ("Geyim kataloqu — Atelier Rental", "Kirayə, hazır geyim və sifarişlə tikilən modellər. Ölçü, rəng və qiymət üzrə kataloqa baxın."),
        "about": ("Haqqımızda — Atelier Rental", "Atelier Rental: tədbirlər, çəkilişlər və xüsusi günlər üçün seçilmiş geyim kolleksiyası və fərdi tikiş xidməti."),
        "contacts": ("Əlaqə — Atelier Rental", "Kirayə, fitting və fərdi sifariş üçün Atelier Rental ilə əlaqə saxlayın."),
    },
    "ru": {
        "home": ("Atelier Rental — аренда одежды в Баку", "Аренда дизайнерской одежды в Баку, готовая коллекция и индивидуальный пошив. Онлайн-бронирование, цвета и 360° обзор."),
        "catalog": ("Каталог одежды — Atelier Rental", "Аренда, готовые изделия и пошив на заказ. Фильтруйте каталог по размеру, цвету и цене."),
        "about": ("О нас — Atelier Rental", "Atelier Rental — коллекция образов для мероприятий, съёмок и особых случаев, а также индивидуальный пошив."),
        "contacts": ("Контакты — Atelier Rental", "Свяжитесь с Atelier Rental по вопросам аренды, примерки и индивидуального заказа."),
    },
    "en": {
        "home": ("Atelier Rental — fashion rental in Baku", "Designer fashion rental in Baku, ready-made pieces and made-to-order service with online booking, colors and 360° viewing."),
        "catalog": ("Fashion catalog — Atelier Rental", "Browse rental, ready-made and made-to-order pieces by size, color and price."),
        "about": ("About — Atelier Rental", "Atelier Rental curates fashion for events, editorials and special occasions alongside made-to-order service."),
        "contacts": ("Contact — Atelier Rental", "Contact Atelier Rental for rental dates, fitting and made-to-order enquiries."),
    },
}

CONTACT_SUCCESS = {
    "az": "Müraciətiniz göndərildi. Tezliklə sizinlə əlaqə saxlayacağıq.",
    "ru": "Заявка отправлена. Мы свяжемся с вами в ближайшее время.",
    "en": "Your request has been sent. We will contact you shortly.",
}
CONTACT_ERROR = {
    "az": "Formada səhvlər var. Sahələri yoxlayın.",
    "ru": "В форме есть ошибки. Проверьте поля.",
    "en": "There are errors in the form. Please check the fields.",
}


def _lang(request):
    lang = request.session.get("site_lang", "az")
    return lang if lang in SUPPORTED_LANGUAGES else "az"


def _seo_context(request, page):
    title, description = SEO_COPY[_lang(request)][page]
    return {"seo_title": title, "seo_description": description}


def _catalog_price_expression():
    return Case(
        When(product_type=Product.RENTAL, then=F("rental_price")),
        When(product_type=Product.READY, then=F("sale_price")),
        When(product_type=Product.CUSTOM, then=F("custom_price")),
        default=None,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def _product_sizes(product):
    return [item.strip() for item in product.sizes.split(",") if item.strip()]


def _localized_product_name(product, lang):
    return {
        "az": product.name_az or product.name_ru,
        "ru": product.name_ru,
        "en": product.name_en,
    }[lang]


def _localized_product_description(product, lang):
    return {
        "az": product.description_az or product.description_ru,
        "ru": product.description_ru,
        "en": product.description_en,
    }[lang]


def _send_mail(subject, body, recipients):
    recipients = [email for email in recipients if email]
    if not recipients:
        return
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )


def _notify_contact(contact, lang):
    _send_mail(
        f"New atelier enquiry — {contact.name}",
        "\n".join([
            f"Name: {contact.name}",
            f"Email: {contact.email}",
            f"Phone: {contact.phone or '-'}",
            "",
            contact.message,
        ]),
        [settings.NOTIFY_EMAIL],
    )
    confirmation = {
        "az": "Müraciətinizi qəbul etdik. Atelier Rental komandası tezliklə sizinlə əlaqə saxlayacaq.",
        "ru": "Мы получили вашу заявку. Команда Atelier Rental свяжется с вами в ближайшее время.",
        "en": "We received your request. The Atelier Rental team will contact you shortly.",
    }[lang]
    _send_mail("Atelier Rental", confirmation, [contact.email])


def _notify_reservation(reservation, lang):
    product_name = _localized_product_name(reservation.product, lang)
    color_name = "-"
    if reservation.color:
        color_name = {
            "az": reservation.color.name_az or reservation.color.name_ru,
            "ru": reservation.color.name_ru,
            "en": reservation.color.name_en,
        }[lang]

    admin_body = "\n".join([
        f"Booking code: {reservation.short_code}",
        f"Product: {reservation.product}",
        f"Color: {reservation.color or '-'}",
        f"Size: {reservation.size or '-'}",
        f"Dates: {reservation.start_date} — {reservation.end_date}",
        f"Customer: {reservation.customer_name}",
        f"Email: {reservation.email}",
        f"Phone: {reservation.phone}",
        f"Notes: {reservation.notes or '-'}",
    ])
    _send_mail(f"New booking {reservation.short_code}", admin_body, [settings.NOTIFY_EMAIL])

    customer_body = {
        "az": f"{product_name} üçün bron sorğunuz qəbul edildi.\nKod: {reservation.short_code}\nRəng: {color_name}\nÖlçü: {reservation.size}\nTarixlər: {reservation.start_date} — {reservation.end_date}\nTəsdiq üçün sizinlə əlaqə saxlayacağıq.",
        "ru": f"Ваша заявка на бронирование «{product_name}» принята.\nКод: {reservation.short_code}\nЦвет: {color_name}\nРазмер: {reservation.size}\nДаты: {reservation.start_date} — {reservation.end_date}\nМы свяжемся с вами для подтверждения.",
        "en": f"Your booking request for {product_name} has been received.\nCode: {reservation.short_code}\nColor: {color_name}\nSize: {reservation.size}\nDates: {reservation.start_date} — {reservation.end_date}\nWe will contact you to confirm it.",
    }[lang]
    _send_mail(f"Atelier Rental — {reservation.short_code}", customer_body, [reservation.email])


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).prefetch_related("images", "colors")[:6]
    rental = Product.objects.filter(is_active=True, product_type=Product.RENTAL).prefetch_related("images", "colors")[:4]
    ready = Product.objects.filter(is_active=True, product_type=Product.READY).prefetch_related("images", "colors")[:4]
    custom = Product.objects.filter(is_active=True, product_type=Product.CUSTOM).prefetch_related("images", "colors")[:4]
    context = {
        "featured": featured,
        "rental": rental,
        "ready": ready,
        "custom": custom,
        **_seo_context(request, "home"),
    }
    if featured and featured[0].cover_image:
        context["seo_image"] = request.build_absolute_uri(featured[0].cover_image.url)
    return render(request, "catalog/home.html", context)


def catalog(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("colors", "images")
        .annotate(catalog_price=_catalog_price_expression())
    )

    product_type = request.GET.get("type", "").strip()
    category = request.GET.get("category", "").strip()
    color = request.GET.get("color", "").strip()
    size = request.GET.get("size", "").strip().upper()
    price_max = request.GET.get("price_max", "").strip()
    sort = request.GET.get("sort", "featured").strip()

    if product_type in {Product.RENTAL, Product.READY, Product.CUSTOM}:
        products = products.filter(product_type=product_type)
    else:
        product_type = ""

    if category:
        products = products.filter(category__slug=category)
    if color.isdigit():
        products = products.filter(colors__id=int(color))
    else:
        color = ""
    if size in {"XS", "S", "M", "L", "XL", "XXL"}:
        products = products.filter(sizes__iregex=rf"(^|,\s*){re.escape(size)}(\s*,|$)")
    else:
        size = ""

    if price_max:
        try:
            max_price = Decimal(price_max)
            if max_price >= 0:
                products = products.filter(catalog_price__lte=max_price)
            else:
                price_max = ""
        except (InvalidOperation, ValueError):
            price_max = ""

    name_sort_field = {"az": "name_az", "ru": "name_ru", "en": "name_en"}[_lang(request)]
    sort_options = {
        "featured": ("-is_featured", "-id"),
        "newest": ("-id",),
        "price_asc": ("catalog_price", "-is_featured"),
        "price_desc": ("-catalog_price", "-is_featured"),
        "name": (name_sort_field, "name_ru"),
    }
    if sort not in sort_options:
        sort = "featured"
    products = products.order_by(*sort_options[sort]).distinct()

    context = {
        "products": products,
        "result_count": products.count(),
        "categories": Category.objects.all(),
        "colors": Color.objects.all(),
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "active_type": product_type,
        "active_category": category,
        "active_color": color,
        "active_size": size,
        "active_price_max": price_max,
        "active_sort": sort,
        **_seo_context(request, "catalog"),
    }
    return render(request, "catalog/catalog.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("colors", "images__color"),
        slug=slug,
        is_active=True,
    )

    media_by_color = {}
    for image in product.images.all():
        key = str(image.color_id or "default")
        bucket = media_by_color.setdefault(key, {"photos": [], "frames": []})
        item = {"id": image.id, "url": image.image.url, "angle": image.angle, "sort": image.sort_order}
        if image.image_type == ProductImage.SPIN_360:
            bucket["frames"].append(item)
        else:
            bucket["photos"].append(item)

    for bucket in media_by_color.values():
        bucket["photos"].sort(key=lambda item: (item["sort"], item["id"]))
        bucket["frames"].sort(key=lambda item: (item["angle"], item["sort"], item["id"]))

    lang = _lang(request)
    product_name = _localized_product_name(product, lang)
    product_description = _localized_product_description(product, lang)
    price = product.rental_price or product.sale_price or product.custom_price
    seo_image = request.build_absolute_uri(product.cover_image.url) if product.cover_image else ""
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_name,
        "description": product_description,
        "url": f"{settings.SITE_URL}{product.get_absolute_url()}",
        "image": [seo_image] if seo_image else [],
        "offers": {
            "@type": "Offer",
            "priceCurrency": "AZN",
            "price": str(price or "0"),
            "availability": "https://schema.org/InStock",
            "url": f"{settings.SITE_URL}{product.get_absolute_url()}",
        },
    }

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "product_sizes": _product_sizes(product),
        "media_by_color": media_by_color,
        "seo_title": f"{product_name} — {settings.SITE_NAME}",
        "seo_description": product_description[:155],
        "seo_image": seo_image,
        "product_schema_json": json.dumps(schema, ensure_ascii=False),
    })


def about(request):
    return render(request, "catalog/about.html", _seo_context(request, "about"))


def contacts(request):
    lang = _lang(request)
    if request.method == "POST":
        if request.POST.get("website"):
            return redirect("contacts")
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            _notify_contact(contact, lang)
            messages.success(request, CONTACT_SUCCESS[lang])
            return redirect("contacts")
        messages.error(request, CONTACT_ERROR[lang])
    else:
        form = ContactForm()
    return render(request, "catalog/contacts.html", {"form": form, **_seo_context(request, "contacts")})


@require_GET
def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"ok": False, "database": "unavailable"}, status=503)
    return JsonResponse({"ok": True, "database": "ok"})


@require_GET
def robots_txt(request):
    base_url = settings.SITE_URL.rstrip("/")
    content = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /ajax/",
        f"Sitemap: {base_url}/sitemap.xml",
    ])
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


@require_POST
def ajax_set_language(request):
    lang = request.POST.get("lang")
    if lang not in SUPPORTED_LANGUAGES:
        return JsonResponse({"ok": False, "error": "unsupported_language"}, status=400)
    request.session["site_lang"] = lang
    return JsonResponse({"ok": True, "lang": lang})


def ajax_booked_dates(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related("colors"),
        pk=product_id,
        is_active=True,
        product_type=Product.RENTAL,
    )
    reservations = product.reservations.filter(
        status__in=[Reservation.PENDING, Reservation.CONFIRMED],
        end_date__gte=date.today(),
    )

    color_id = request.GET.get("color", "").strip()
    if product.colors.exists():
        if not color_id.isdigit() or not product.colors.filter(pk=int(color_id)).exists():
            return JsonResponse({"ranges": [], "error": "invalid_color"}, status=400)
        reservations = reservations.filter(color_id=int(color_id))
    else:
        reservations = reservations.filter(color__isnull=True)

    ranges = [
        {"start": reservation.start_date.isoformat(), "end": reservation.end_date.isoformat()}
        for reservation in reservations.only("start_date", "end_date")
    ]
    return JsonResponse({"ranges": ranges, "today": date.today().isoformat()})


@require_POST
def ajax_reserve(request, product_id):
    form = ReservationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "error": "invalid_form", "errors": form.errors.get_json_data()}, status=400)

    try:
        with transaction.atomic():
            product = get_object_or_404(
                Product.objects.select_for_update().prefetch_related("colors"),
                pk=product_id,
                is_active=True,
                product_type=Product.RENTAL,
            )
            reservation = form.save(commit=False)
            reservation.product = product
            reservation.full_clean()
            reservation.save()
    except ValidationError as exc:
        errors = getattr(exc, "message_dict", {"__all__": exc.messages})
        return JsonResponse({"ok": False, "error": "validation_error", "errors": errors}, status=409)

    _notify_reservation(reservation, _lang(request))
    return JsonResponse({
        "ok": True,
        "reservation_id": reservation.id,
        "booking_code": reservation.short_code,
        "status": reservation.status,
        "start": reservation.start_date.isoformat(),
        "end": reservation.end_date.isoformat(),
    })
