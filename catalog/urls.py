from django.urls import path

from . import account_views, views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("login/", account_views.login_register, name="login"),
    path("logout/", account_views.logout_view, name="logout"),
    path("wishlist/", account_views.wishlist, name="wishlist"),
    path("healthz/", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("ajax/language/", views.ajax_set_language, name="ajax_set_language"),
    path("ajax/favorites/<int:product_id>/toggle/", account_views.toggle_favorite, name="toggle_favorite"),
    path("ajax/products/<int:product_id>/booked-dates/", views.ajax_booked_dates, name="ajax_booked_dates"),
    path("ajax/products/<int:product_id>/reserve/", views.ajax_reserve, name="ajax_reserve"),
]
