from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import EmailLoginForm, RegisterForm
from .models import Favorite, Product


AUTH_COPY = {
    "az": {"login_ok": "Xoş gəlmisiniz.", "register_ok": "Hesabınız yaradıldı.", "logout_ok": "Hesabdan çıxdınız."},
    "ru": {"login_ok": "Вы вошли в аккаунт.", "register_ok": "Аккаунт создан.", "logout_ok": "Вы вышли из аккаунта."},
    "en": {"login_ok": "Welcome back.", "register_ok": "Your account has been created.", "logout_ok": "You have signed out."},
}


def _lang(request):
    lang = request.session.get("site_lang", "az")
    return lang if lang in AUTH_COPY else "az"


def _safe_next(request, value, fallback):
    if value and url_has_allowed_host_and_scheme(value, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return value
    return fallback


def login_register(request):
    lang = _lang(request)
    fallback = reverse("wishlist")
    next_value = request.POST.get("next") or request.GET.get("next") or fallback
    next_url = _safe_next(request, next_value, fallback)
    if request.user.is_authenticated and request.method == "GET":
        return redirect(next_url)
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
    titles = {"az": "Giriş və qeydiyyat — JALUZINO COUTURE", "ru": "Вход и регистрация — JALUZINO COUTURE", "en": "Login & registration — JALUZINO COUTURE"}
    descriptions = {"az": "JALUZINO COUTURE hesabınıza daxil olun və ya yeni hesab yaradın.", "ru": "Войдите в JALUZINO COUTURE или создайте новый аккаунт.", "en": "Sign in to JALUZINO COUTURE or create a new account."}
    return render(request, "catalog/account.html", {"login_form": login_form, "register_form": register_form, "next_url": next_url, "seo_title": titles[lang], "seo_description": descriptions[lang]})


@require_POST
def logout_view(request):
    lang = _lang(request)
    logout(request)
    messages.success(request, AUTH_COPY[lang]["logout_ok"])
    return redirect("home")


@login_required(login_url="login")
def wishlist(request):
    products = Product.objects.filter(is_active=True, favorites__user=request.user).select_related("category").prefetch_related("colors", "images").order_by("-favorites__created_at").distinct()
    lang = _lang(request)
    titles = {"az": "Seçilmişlər — JALUZINO COUTURE", "ru": "Избранное — JALUZINO COUTURE", "en": "Wishlist — JALUZINO COUTURE"}
    return render(request, "catalog/wishlist.html", {"products": products, "seo_title": titles[lang], "seo_description": titles[lang]})


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
    return JsonResponse({"ok": True, "is_favorite": is_favorite, "count": request.user.favorites.count()})
