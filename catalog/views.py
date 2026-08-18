import json
from datetime import date

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ContactForm, ReservationForm
from .models import Category, Product, Reservation


def _lang(request):
    lang = request.session.get("site_lang", "ru")
    return lang if lang in {"ru", "en"} else "ru"


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:6]
    ready = Product.objects.filter(is_active=True, product_type=Product.READY)[:4]
    custom = Product.objects.filter(is_active=True, product_type=Product.CUSTOM)[:4]
    return render(request, "catalog/home.html", {"featured": featured, "ready": ready, "custom": custom})


def catalog(request):
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("colors")
    product_type = request.GET.get("type")
    category = request.GET.get("category")
    if product_type in {Product.READY, Product.CUSTOM}:
        products = products.filter(product_type=product_type)
    if category:
        products = products.filter(category__slug=category)
    return render(request, "catalog/catalog.html", {
        "products": products,
        "categories": Category.objects.all(),
        "active_type": product_type or "",
        "active_category": category or "",
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related("colors", "images__color"), slug=slug, is_active=True)
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
    product = get_object_or_404(Product, pk=product_id)
    reservations = product.reservations.filter(
        status__in=[Reservation.PENDING, Reservation.CONFIRMED],
        end_date__gte=date.today(),
    ).values("start_date", "end_date")
    ranges = [{"start": r["start_date"].isoformat(), "end": r["end_date"].isoformat()} for r in reservations]
    return JsonResponse({"ranges": ranges})


@require_POST
def ajax_reserve(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
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
