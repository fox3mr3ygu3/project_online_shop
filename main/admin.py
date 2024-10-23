from django.contrib import admin, messages
from django.utils.text import slugify  
from .models import Product, Image, SortedProducts, Category, Brand
from django.core.exceptions import ValidationError
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class SortedProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        js = ('main/scripts/admin.js',)  # Подключаем кастомный JS

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
    
    def save_model(self, request, obj, form, change):
        obj.slug = slugify(obj.title)  # Generate slug from title every time
        super().save_model(request, obj, form, change)

        try:
            obj.clean()  # Проверяем данные перед сохранением
        except ValidationError as e:
            self.message_user(request, str(e), level=messages.ERROR)
            return  # Не сохраняем объект, если данные невалидные

        # Сохраняем объект
        super().save_model(request, obj, form, change)

admin.site.register(Product, ProductAdmin)
admin.site.register(Image)
admin.site.register(SortedProducts, SortedProductsAdmin)
admin.site.register(Category)
admin.site.register(Brand)
