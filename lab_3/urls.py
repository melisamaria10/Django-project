from django.urls import path
from . import views
from lab_3.sitemaps import MasinaSitemap, VederiStaticeSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'masini': MasinaSitemap,
    'static': VederiStaticeSitemap,
}

urlpatterns = [
    path("", views.index, name="index"),
    path("contact", views.contact_view, name="formular"), ##task2 lab 5
    path("mesaj_trimis", views.mesaj_trimis_view, name="succes"),
    path("creare_masina", views.creare_masina, name='creare_masina'), ##task3 lab5
    path("list", views.listing, name="listare_masini"), ##task2 lab4 paginarea
    path("masina_list", views.masina_list, name="filtrare_masini"), ##task2 lab4
    path("masina_filter", views.masina_filter, name="filtrare"),  ##task1 lab5
    path("inregistrare", views.register_view, name="inregistrare"),
    path("login", views.custom_login_view, name="login"),
    path("schimba_parola", views.change_password_view, name="schimba_parola"),
    path("profil", views.profile_view, name="profil"),
    path("logout", views.logout_view, name="logout"),
    path("confirmare_succes/<str:cod>/", views.confirma_mail, name="confirmare_succes"), ### task 1 lab 7
    path("promotii", views.promotii_view, name="promotii"),
    path("pagina", views.afisare_pagina2, name="pagina"),
    path('adauga_permisiune_oferta', views.adauga_permisiune_oferta, name='adauga_permisiune_oferta'),
    path("oferta", views.oferta, name="oferta"),
    path("masina/json/<int:id>", views.masina_detail_json, name="masina_detail_json"),
    path("masina/<int:id>", views.masina_detail, name="masina_detail"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path("cos_virtual", views.cos_virtual, name="cos_virtual"), 
    path("procesare_date", views.procesare_date, name="procesare_date"),
]