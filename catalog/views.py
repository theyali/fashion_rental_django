import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Case, DecimalField, F, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ContactForm, ReservationForm
from .models import Category, Color, Product, Reservation


def _lang(request):
    lang = request.session.get("site_lang", "ru")
    return lang if lang in {"ru", "en"} else "ru"


def _catalog_price_expression():
    return Case(
        When(product_type=Product.RENTAL, then=F("rental_price")),
        When(product_type=Product.READY, then=F("sale_price")),
        When(product_type=Product.CUSTOM, then=F("custom_price")),
        default=None,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).prefetch_related("images", "colors")[:6]
    rental = Product.objects.filter(is_active=True, product_type=Product.RENTAL).prefetch_related("images", "colors")[:4]
    ready = Product.objects.filter(is_active=True, product_type=Product.READY).prefetch_related("images", "colors")[:4]
    custom = Product.objects.filter(is_active=True, product_type=Product.CUSTOM).prefetch_related("images", "colors")[:4]
    return render(request, "catalog/home.html", {
        "featured": featured,
        "rental": rental,
        "ready": ready,
        "custom": custom,
    })


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
        products = products.filter(sizes__icontains=size)
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

    sort_options = {
        "featured": ("-is_featured", "-id"),
        "newest": ("-id",),
        "price_asc": ("catalog_price", "-is_featured"),
        "price_desc": ("-catalog_price", "-is_featured"),
        "name": ("name_ru",),
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
    }
    return render(request, "catalog/catalog.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("colors", "images__color"),
        slug=slug,
        is_active=True,
    )
    frames_by_color = {}
    for image in product.images.all():
        key = str(image.color_id or "default")
        frames_by_color.setdefault(key, []).append({"angle": image.angle, "url": image.image.url})
    for frames in frames_by_color.values():
        frames.sort(key=lambda x: x["angle"])
    return render(request, "catalog/product_detail.html", {
        "product": product,
        "frames_json": json.dumps(frames_by_color),
    })


def about(request):
    return render(request, "catalog/about.html")


def contacts(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contacts")
    else:
        form = ContactForm()
    return render(request, "catalog/contacts.html", {"form": form})


@require_POST
def ajax_set_language(request):
    lang = request.POST.get("lang")
    if lang not in {"ru", "en"}:
        return JsonResponse({"ok": False, "error": "Unsupported language"}, status=400)
    request.session["site_lang"] = lang
    return JsonResponse({"ok": True, "lang": lang})


def ajax_booked_dates(request, product_id):
    product = get_object_or_404(Product, pk=product_id, product_type=Product.RENTAL)
    reservations = product.reservations.filter(
        status__in=[Reservation.PENDING, Reservation.CONFIRMED],
        end_date__gte=date.today(),
    ).values("start_date", "end_date")
    ranges = [{"start": r["start_date"].isoformat(), "end": r["end_date"].isoformat()} for r in reservations]
    return JsonResponse({"ranges": ranges})


@require_POST
def ajax_reserve(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True, product_type=Product.RENTAL)
    form = ReservationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)
    reservation = form.save(commit=False)
    reservation.product = product
    try:
        reservation.full_clean()
        reservation.save()
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": " ".join(exc.messages)}, status=409)
    return JsonResponse({"ok": True, "reservation_id": reservation.id})
