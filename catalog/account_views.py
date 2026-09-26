from urllib.parse import urlencode
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import EmailLoginForm, ProductSubmissionForm, RegisterForm
from .models import Favorite, Product, ProductImage, ProductVideo


AUTH_COPY = {
    "az": {"login_ok": "Xoş gəlmisiniz.", "register_ok": "Hesabınız yaradıldı.", "logout_ok": "Hesabdan çıxdınız.", "submit_ok": "Elanınız moderasiyaya göndərildi."},
    "ru": {"login_ok": "Вы вошли в аккаунт.", "register_ok": "Аккаунт создан.", "logout_ok": "Вы вышли из аккаунта.", "submit_ok": "Объявление отправлено на модерацию."},
    "en": {"login_ok": "Welcome back.", "register_ok": "Your account has been created.", "logout_ok": "You have signed out.", "submit_ok": "Your listing has been sent for moderation."},
}


def _lang(request):
    lang = request.session.get("site_lang", "az")
    return lang if lang in AUTH_COPY else "az"


def _safe_next(request, value, fallback):
    if value and url_has_allowed_host_and_scheme(value, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return value
    return fallback


def _unique_product_slug(name):
    base = slugify(name, allow_unicode=True) or "dress"
    slug = base[:44].strip("-")
    candidate = slug
    while Product.objects.filter(slug=candidate).exists():
        candidate = f"{slug}-{uuid4().hex[:6]}"
    return candidate


def login_register(request):
    lang = _lang(request)
    fallback = reverse("account")
    next_value = request.POST.get("next") or request.GET.get("next") or fallback
    next_url = _safe_next(request, next_value, fallback)

    if request.user.is_authenticated and request.method == "GET":
        return redirect("account")

    login_form = EmailLoginForm(request=request)
    register_form = RegisterForm()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "login":
            login_form = EmailLoginForm(request.POST, request=request)
            if login_form.is_valid():
                login(request, login_form.get_user())
                messages.success(request, AUTH_COPY[lang]["login_ok"])
                return redirect(next_url)
        elif action == "register":
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, AUTH_COPY[lang]["register_ok"])
                return redirect(next_url)

    titles = {
        "az": "Giriş və qeydiyyat — JALIZINO COUTURE",
        "ru": "Вход и регистрация — JALIZINO COUTURE",
        "en": "Login & registration — JALIZINO COUTURE",
    }
    descriptions = {
        "az": "JALIZINO COUTURE hesabınıza daxil olun və ya yeni hesab yaradın.",
        "ru": "Войдите в JALIZINO COUTURE или создайте новый аккаунт.",
        "en": "Sign in to JALIZINO COUTURE or create a new account.",
    }
    return render(
        request,
        "catalog/account.html",
        {
            "login_form": login_form,
            "register_form": register_form,
            "next_url": next_url,
            "seo_title": titles[lang],
            "seo_description": descriptions[lang],
        },
    )


@login_required(login_url="login")
def account_dashboard(request):
    lang = _lang(request)
    titles = {
        "az": "Hesabım — JALIZINO COUTURE",
        "ru": "Мой аккаунт — JALIZINO COUTURE",
        "en": "My account — JALIZINO COUTURE",
    }
    descriptions = {
        "az": "JALIZINO COUTURE şəxsi hesabı.",
        "ru": "Личный аккаунт JALIZINO COUTURE.",
        "en": "Your JALIZINO COUTURE account.",
    }
    return render(
        request,
        "catalog/account_dashboard.html",
        {
            "favorite_count": request.user.favorites.count(),
            "submitted_products": request.user.submitted_products.select_related("category").order_by("-created_at")[:8],
            "seo_title": titles[lang],
            "seo_description": descriptions[lang],
        },
    )


@login_required(login_url="login")
def submit_product(request):
    lang = _lang(request)
    form = ProductSubmissionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        listing_type = data["listing_type"]
        is_rentable = listing_type in {ProductSubmissionForm.LISTING_RENTAL, ProductSubmissionForm.LISTING_BOTH}
        is_purchasable = listing_type in {ProductSubmissionForm.LISTING_SALE, ProductSubmissionForm.LISTING_BOTH}
        product = Product.objects.create(
            owner=request.user,
            source=Product.SOURCE_USER,
            moderation_status=Product.MODERATION_PENDING,
            is_active=False,
            category=data["category"],
            slug=_unique_product_slug(data["name"]),
            name_az=data["name"],
            name_ru=data["name"],
            name_en=data["name"],
            brand=data.get("brand") or "",
            description_az=data["description"],
            description_ru=data["description"],
            description_en=data["description"],
            material_az=data.get("material") or "",
            material_ru=data.get("material") or "",
            material_en=data.get("material") or "",
            length_az=data.get("length") or "",
            length_ru=data.get("length") or "",
            length_en=data.get("length") or "",
            care_az=data.get("care") or "",
            care_ru=data.get("care") or "",
            care_en=data.get("care") or "",
            extra_details_az=data.get("extra_details") or "",
            extra_details_ru=data.get("extra_details") or "",
            extra_details_en=data.get("extra_details") or "",
            additional_note_az=data.get("additional_note") or "",
            additional_note_ru=data.get("additional_note") or "",
            additional_note_en=data.get("additional_note") or "",
            product_type=Product.RENTAL if is_rentable else Product.READY,
            is_rentable=is_rentable,
            is_purchasable=is_purchasable,
            rental_price=data.get("rental_price") if is_rentable else None,
            sale_price=data.get("sale_price") if is_purchasable else None,
            min_rental_days=data.get("min_rental_days") or 3,
            sizes=data["sizes"],
        )
        product.colors.set(data["colors"])
        images = data["images"]
        if images:
            product.cover_image = images[0]
            product.save(update_fields=["cover_image"])
            for index, image in enumerate(images):
                ProductImage.objects.create(product=product, image=image, sort_order=index)
        for index, video in enumerate(data.get("videos") or []):
            ProductVideo.objects.create(product=product, video=video, sort_order=index)
        messages.success(request, AUTH_COPY[lang]["submit_ok"])
        return redirect("account")

    titles = {
        "az": "Elan əlavə et — JALIZINO COUTURE",
        "ru": "Добавить объявление — JALIZINO COUTURE",
        "en": "Add listing — JALIZINO COUTURE",
    }
    return render(request, "catalog/product_submit.html", {"form": form, "seo_title": titles[lang], "seo_description": titles[lang]})


@require_POST
def logout_view(request):
    lang = _lang(request)
    logout(request)
    messages.success(request, AUTH_COPY[lang]["logout_ok"])
    return redirect("home")


@login_required(login_url="login")
def wishlist(request):
    products = (
        Product.objects.filter(is_active=True, favorites__user=request.user)
        .select_related("category")
        .prefetch_related("colors", "images")
        .order_by("-favorites__created_at")
        .distinct()
    )
    lang = _lang(request)
    titles = {
        "az": "Seçilmişlər — JALIZINO COUTURE",
        "ru": "Избранное — JALIZINO COUTURE",
        "en": "Wishlist — JALIZINO COUTURE",
    }
    return render(
        request,
        "catalog/wishlist.html",
        {"products": products, "seo_title": titles[lang], "seo_description": titles[lang]},
    )


@require_POST
def toggle_favorite(request, product_id):
    next_value = request.POST.get("next") or "/"
    next_url = _safe_next(request, next_value, "/")
    if not request.user.is_authenticated:
        login_url = f"{reverse('login')}?{urlencode({'next': next_url})}"
        return JsonResponse({"ok": False, "auth_required": True, "login_url": login_url}, status=401)

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if created:
        is_favorite = True
    else:
        favorite.delete()
        is_favorite = False

    return JsonResponse(
        {"ok": True, "is_favorite": is_favorite, "count": request.user.favorites.count()}
    )
