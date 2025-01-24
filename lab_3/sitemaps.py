from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from lab_3.models import Masina

### TASK 2 LA 9 SITEMAP ###
class MasinaSitemap(Sitemap):
    changefreq="monthly"
    priority=0.7
    
    def items(self):
        return Masina.objects.all()
    
    def location(self, obj):
        return obj.get_absolute_url()
    
class VederiStaticeSitemap(Sitemap):
    changefreq="monthly"
    priority= 0.6
    def items(self):
        return ['formular']

    def location(self, item):
        return reverse(item)

