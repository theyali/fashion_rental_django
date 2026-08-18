from django.conf import settings
from django.db import DatabaseError, OperationalError, ProgrammingError

from .models import SiteSettings


DEFAULT_DESCRIPTIONS = {
    "az": "Bakıda dizayner geyimlərinin kirayəsi, hazır kolleksiya və fərdi tikiş. Rəng seçimi, 360° baxış və onlayn bron.",
    "ru": "Аренда дизайнерской одежды в Баку, готовая коллекция и индивидуальный пошив. Выбор цвета, 360° обзор и онлайн-бронирование.",
    "en": "Designer fashion rental in Baku, ready-made pieces and made-to-order service with color selection, 360° view and online booking.",
}


def _site_settings():
    try:
        return SiteSettings.objects.filter(pk=1).first()
    except (DatabaseError, OperationalError, ProgrammingError):
        return None


def global_site_context(request):
    lang = request.session.get("site_lang", "az")
    if lang not in DEFAULT_DESCRIPTIONS:
        lang = "az"
    site = _site_settings()
    base_url = settings.SITE_URL.rstrip("/")
    canonical_url = f"{base_url}{request.path}"
    og_locale = {"az": "az_AZ", "ru": "ru_RU", "en": "en_US"}[lang]
    site_name = site.brand_name if site and site.brand_name else "JALUZINO COUTURE"
    contact_email = site.contact_email if site and site.contact_email else settings.CONTACT_EMAIL
    contact_phone = site.contact_phone if site and site.contact_phone else settings.CONTACT_PHONE
    contact_location = site.localized_location(lang) if site else settings.CONTACT_LOCATION
    whatsapp_url = site.whatsapp_url(lang) if site else ""
    whatsapp_label = site.localized_whatsapp_label(lang) if site else ""
    social_links = []
    if site:
        for key, name, url in (("instagram", "Instagram", site.instagram_url), ("facebook", "Facebook", site.facebook_url), ("tiktok", "TikTok", site.tiktok_url), ("youtube", "YouTube", site.youtube_url), ("pinterest", "Pinterest", site.pinterest_url)):
            if url:
                social_links.append({"key": key, "name": name, "url": url})
    favorite_product_ids = set()
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            favorite_product_ids = set(request.user.favorites.values_list("product_id", flat=True))
            wishlist_count = len(favorite_product_ids)
        except (DatabaseError, OperationalError, ProgrammingError):
            pass
    return {
        "site_settings": site,
        "site_name": site_name,
        "site_url": base_url,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "contact_location": contact_location,
        "whatsapp_url": whatsapp_url,
        "whatsapp_label": whatsapp_label,
        "social_links": social_links,
        "favorite_product_ids": favorite_product_ids,
        "wishlist_count": wishlist_count,
        "canonical_url": canonical_url,
        "seo_title": site_name,
        "seo_description": DEFAULT_DESCRIPTIONS[lang],
        "seo_image": "",
        "og_locale": og_locale,
    }
