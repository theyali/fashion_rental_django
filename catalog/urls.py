from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("ajax/language/", views.ajax_set_language, name="ajax_set_language"),
    path("ajax/products/<int:product_id>/booked-dates/", views.ajax_booked_dates, name="ajax_booked_dates"),
    path("ajax/products/<int:product_id>/reserve/", views.ajax_reserve, name="ajax_reserve"),
]
