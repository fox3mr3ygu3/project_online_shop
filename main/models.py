from django.db import models
from django.utils.safestring import mark_safe
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError


class VisitorCounter(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Visitor count: {self.count}"


class Image(models.Model):
    image = models.ImageField(upload_to='images')
    title = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.image}"


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ManyToManyField(Image, blank=True)

    def __str__(self):
        return f"{self.title}"


class Category(models.Model):
    category = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.category}"


class Brand(models.Model):
    brand = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.brand}"
    


class SortedProducts(models.Model):
    title = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    fps = models.PositiveIntegerField(null=True, blank=True)  # Optional fps field
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = MoneyField(max_digits=20, default_currency='UZS')
    image = models.ManyToManyField(Image, blank=True)

    def clean(self):
        # Проверяем наличие fps для категории 'monitor'
        if self.category.category.lower() == 'monitor' and not self.fps:
            raise ValidationError('Поле FPS обязательно для категории "monitor".')

    def safe_description(self):
        return mark_safe(self.description.replace('\n', '<br>'))

    class Meta:
        verbose_name_plural = "Sorted Products"

    def __str__(self):
        return f"{self.title}"