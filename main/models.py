from django.db import models
from django.utils.safestring import mark_safe
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError, ObjectDoesNotExist


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
    # Абстрактные поля для категорий
    resolution = models.CharField(max_length=50, null=True, blank=True)  # Разрешение (Монитор)
    switch_type = models.CharField(max_length=50, null=True, blank=True)  # Тип переключателей (Клавиатура)
    backlight = models.BooleanField(null=True, blank=True)  # Подсветка (Клавиатура, коврик для мыши)
    dpi = models.PositiveIntegerField(null=True, blank=True)  # DPI (Мышь)
    sensor_type = models.CharField(max_length=50, null=True, blank=True)  # Тип сенсора (Мышь)
    socket_type = models.CharField(max_length=50, null=True, blank=True)  # Сокет CPU (Материнская плата)
    form_factor = models.CharField(max_length=50, null=True, blank=True)  # Форм-фактор (Материнская плата, Корпус)
    ram_type = models.CharField(max_length=50, null=True, blank=True)  # Тип RAM (ОЗУ)
    ram_size = models.PositiveIntegerField(null=True, blank=True)  # Объем RAM (ОЗУ)
    power_wattage = models.PositiveIntegerField(null=True, blank=True)  # Мощность (Блок питания)
    certification = models.CharField(max_length=50, null=True, blank=True)  # Сертификация (Блок питания)
    storage_type = models.CharField(max_length=50, null=True, blank=True)  # Тип (SSD/HDD)
    storage_size = models.PositiveIntegerField(null=True, blank=True)  # Объем памяти (Хранение)
    cooling_type = models.CharField(max_length=50, null=True, blank=True)  # Тип охлаждения (Охлаждение)
    video_memory = models.PositiveIntegerField(null=True, blank=True)  # Память (Видеокарта)
    connection_type = models.CharField(max_length=50, null=True, blank=True)  # Подключение (Наушники)
    noise_cancellation = models.BooleanField(null=True, blank=True)  # Шумоподавление (Наушники)
    mouse_pad_size = models.CharField(max_length=50, null=True, blank=True)  # Размер (Коврик для мыши)

    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = MoneyField(max_digits=20, default_currency='UZS')
    image = models.ManyToManyField(Image, blank=True)

    def clean(self):
        # Проверка обязательных полей для категории 'monitor'
        if self.category.category.lower() == 'monitor':
            if not self.fps:
                raise ValidationError('Поле FPS обязательно для категории "monitor".')
            if not self.resolution:
                raise ValidationError('Поле разрешения обязательно для категории "monitor".')

        # Проверка обязательных полей для категории 'keyboard'
        if self.category.category.lower() == 'keyboard':
            if not self.switch_type:
                raise ValidationError('Поле типа переключателей обязательно для категории "keyboard".')
            if self.backlight is None:
                raise ValidationError('Поле подсветки обязательно для категории "keyboard".')

        # Проверка обязательных полей для категории 'mouse'
        if self.category.category.lower() == 'mouse':
            if not self.dpi:
                raise ValidationError('Поле DPI обязательно для категории "mouse".')
            if not self.sensor_type:
                raise ValidationError('Поле типа сенсора обязательно для категории "mouse".')

        # Проверка обязательных полей для категории 'motherboard'
        if self.category.category.lower() == 'motherboard':
            if not self.socket_type:
                raise ValidationError('Поле сокета CPU обязательно для категории "motherboard".')
            if not self.form_factor:
                raise ValidationError('Поле форм-фактора обязательно для категории "motherboard".')

        # Проверка обязательных полей для категории 'ram'
        if self.category.category.lower() == 'ram':
            if not self.ram_type:
                raise ValidationError('Поле типа RAM обязательно для категории "ram".')
            if not self.ram_size:
                raise ValidationError('Поле объема RAM обязательно для категории "ram".')

        # Проверка обязательных полей для категории 'power supply'
        if self.category.category.lower() == 'power-supply':
            if not self.power_wattage:
                raise ValidationError('Поле мощности обязательно для категории "power supply".')
            if not self.certification:
                raise ValidationError('Поле сертификации обязательно для категории "power supply".')

        # Проверка обязательных полей для категории 'storage'
        if self.category.category.lower() == 'storage':
            if not self.storage_type:
                raise ValidationError('Поле типа (SSD/HDD) обязательно для категории "storage".')
            if not self.storage_size:
                raise ValidationError('Поле объема памяти обязательно для категории "storage".')

        # Проверка обязательных полей для категории 'cooling'
        if self.category.category.lower() == 'cooling':
            if not self.cooling_type:
                raise ValidationError('Поле типа охлаждения обязательно для категории "cooling".')

        # Проверка обязательных полей для категории 'graphics card'
        if self.category.category.lower() == 'graphics card':
            if not self.video_memory:
                raise ValidationError('Поле объема видеопамяти обязательно для категории "graphics card".')
            if not self.ram_type:
                raise ValidationError('Поле типа памяти обязательно для категории "graphics card".')

        # Проверка обязательных полей для категории 'headphones'
        if self.category.category.lower() == 'headphones':
            if not self.connection_type:
                raise ValidationError('Поле подключения обязательно для категории "headphones".')
            if self.noise_cancellation is None:
                raise ValidationError('Поле шумоподавления обязательно для категории "headphones".')

        # Проверка обязательных полей для категории 'mouse pad'
        if self.category.category.lower() == 'mouse pad':
            if not self.mouse_pad_size:
                raise ValidationError('Поле размера обязательно для категории "mouse pad".')

        # Проверка обязательных полей для категории 'case'
        if self.category.category.lower() == 'case':
            if not self.form_factor:
                raise ValidationError('Поле форм-фактора обязательно для категории "case".')

    def safe_description(self):
        return mark_safe(self.description.replace('\n', '<br>'))

    class Meta:
        verbose_name_plural = "Sorted Products"

    def __str__(self):
        return f"{self.title}"


class Order(models.Model):
    quantity = models.IntegerField()
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    telegram = models.CharField(max_length=100, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)  # Дата создания заказа
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Общая стоимость заказа
    product_name = models.CharField(max_length=250)
    
    