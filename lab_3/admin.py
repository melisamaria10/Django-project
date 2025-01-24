from django.contrib import admin
from lab_3.models import Masina, Categorie, Caracteristici, Dealer, Revizie, TipMotor, CustomUser, Vizualizare

# Register your models here.

class TipMotorAdmin(admin.ModelAdmin):
    list_display=('tip_motor',)
    
class CategorieAdmin(admin.ModelAdmin):
    list_display=('nume', 'descriere','get_tipuri_motor')
    filter_horizontal=('tipuri_motor',)

class RevizieInline(admin.TabularInline):
    model = Revizie
    extra = 1  
    
class MasinaAdmin(admin.ModelAdmin):
    list_display=('marca','model','imagine','an_fabricatie','kilometraj','pret','categorie','tip_motor', 'stoc')
    list_filter=('an_fabricatie','pret')
    search_field=('marca','an_fabricatie')
    filter_horizontal = ('caracteristici',)
    fieldsets = (
        (None, {
            'fields': ('marca', 'model', 'an_fabricatie','tip_motor', 'stoc')
        }),
        ('Detalii', {
            'fields': ('kilometraj', 'pret', 'categorie', 'dealer', 'imagine'),
            'description': 'Detalii suplimentare despre masina',
            'classes': ('collapse',)  
        }),
        ('Caracteristici', {
            'fields': ('caracteristici',),  
            'description': 'Caracteristicile mașinii',
            'classes': ('collapse',)  
        }),
    )
    inlines=[RevizieInline]
    
class CaracteristiciAdmin(admin.ModelAdmin):
    list_display=('nume','descriere')
    
class DealerAdmin(admin.ModelAdmin):
    list_display=('email','telefon','locatie')
    search_field=('locatie')
    
class RevizieAdmin(admin.ModelAdmin):
    list_display=('masina','serviciu','data_revizie','nr_kilometri','cost')
    search_fields=('data_revizie',)
    
### TASK 2 LAB 7 ###
class VizualizareAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change) 
        N = 5  
        vizualizari = Vizualizare.objects.filter(user=obj.user).order_by('-data_vizualizare')
        if vizualizari.count() > N:
            vizualizari_to_delete = vizualizari[N:] 
            Vizualizare.objects.filter(id__in=[v.id for v in vizualizari_to_delete]).delete()
            
### TASK 2 LAB 8 ###

from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model= CustomUser
    fieldsets = (
            (None, {'fields': ('telefon', 'data_nasterii', 'adresa', 'gen', 'cod_postal', 'email_confirmat', 'blocat')}),
    ) + UserAdmin.fieldsets 
    
admin.site.register(Masina, MasinaAdmin)
admin.site.register(Categorie,CategorieAdmin)
admin.site.register(Caracteristici,CaracteristiciAdmin)
admin.site.register(Dealer,DealerAdmin)
admin.site.register(Revizie,RevizieAdmin)
admin.site.register(TipMotor,TipMotorAdmin)
admin.site.register(Vizualizare, VizualizareAdmin)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.site_header="Panou de Administrare Site"
admin.site.site_title="Admin Site"
admin.site.index_title="Bine ai venit!"
