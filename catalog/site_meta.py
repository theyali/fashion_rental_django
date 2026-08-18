from django.conf import settings


DEFAULT_DESCRIPTIONS = {
    "az": "Bakıda dizayner geyimlərinin kirayəsi, hazır kolleksiya və fərdi tikiş. Rəng seçimi, 360° baxış və onlayn bron.",
    "ru": "Аренда дизайнерской одежды в Баку, готовая коллекция и индивидуальный пошив. Выбор цвета, 360° обзор и онлайн-бронирование.",
    "en": "Designer fashion rental in Baku, ready-made pieces and made-to-order service with color selection, 360° view and online booking.",
}


def global_site_context(request):
    lang = request.session.get("site_lang", "az")
    if lang not in DEFAULT_DESCRIPTIONS:
        lang = "az"

    base_url = settings.SITE_URL.rstrip("/")
    canonical_url = f"{base_url}{request.path}"
    og_locale = {"az": "az_AZ", "ru": "ru_RU", "en": "en_US"}[lang]

    return {
        "site_name": settings.SITE_NAME,
        "site_url": base_url,
        "contact_email": settings.CONTACT_EMAIL,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_location": settings.CONTACT_LOCATION,
        "canonical_url": canonical_url,
        "seo_title": settings.SITE_NAME,
        "seo_description": DEFAULT_DESCRIPTIONS[lang],
        "seo_image": "",
        "og_locale": og_locale,
    }
