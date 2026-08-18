from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True).order_by("id")

    def lastmod(self, obj):
        return obj.created_at


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return ["home", "catalog", "about", "contacts"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {"home": 1.0, "catalog": 0.9, "about": 0.5, "contacts": 0.5}.get(item, 0.5)
