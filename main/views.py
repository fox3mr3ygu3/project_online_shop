from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, SortedProducts, Category, Brand, VisitorCounter, Order
from django.utils.text import slugify
from django.db.models import Min, Max, F
from django.http import JsonResponse
from fuzzywuzzy import process
from django.utils import timezone
from datetime import timedelta
from .telegram_bot import send_order_to_telegram



def home(request):
    products = Product.objects.all()
    visitor_counter = VisitorCounter.objects.get(id=1)

    # Получаем текущее время
    current_time = timezone.now()

    # Проверяем, есть ли в сессии время последнего обновления
    last_visit_time_str = request.session.get('last_visit_time')

    if last_visit_time_str:
        # Преобразуем строку обратно в datetime
        last_visit_time = timezone.datetime.fromisoformat(last_visit_time_str)
    else:
        last_visit_time = None

    # Если пользователь посещает страницу впервые или прошло больше 60 секунд
    if last_visit_time is None or current_time - last_visit_time > timedelta(seconds=60):
        # Увеличиваем счетчик
        visitor_counter.count += 1
        visitor_counter.save()

        # Обновляем время последнего посещения в сессии
        request.session['last_visit_time'] = current_time.isoformat()

    # Получаем текущее значение счетчика
    visitor_count = visitor_counter.count

    return render(request, 'main/home.html', {
        'products': products,
        'visitor_count': visitor_count
    })


def get_visitor_count(request):
    # Возвращаем текущее значение счетчика в формате JSON
    visitor_count = VisitorCounter.objects.get(id=1).count
    return JsonResponse({'visitor_count': visitor_count})


def buy(request, product_category, product_slug):
    selected_product = SortedProducts.objects.get(slug=product_slug, category__category=product_category)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        name = request.POST.get('name')  # Получаем Имя
        city = request.POST.get('city')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        telegram = request.POST.get('telegram')  # Получаем Telegram
        total_price = selected_product.price.amount * quantity   # Рассчитываем общую стоимость

        order = Order.objects.create(
            quantity=quantity,
            name=name,
            city=city,
            address=address,
            phone=phone,
            telegram=telegram,
            total_price=total_price,
            product_name=selected_product
        )
        print('12')
        response = send_order_to_telegram(order) # Отправляем заказ на Тelegram 
        if response.status_code == 200:
            # Устанавливаем флаг в сессии после успешной покупки
            request.session['purchase_successful'] = True
            return redirect('final-page', product_category=product_category, product_slug=product_slug)  # Перенаправление на страницу успешного заказа
        else:
        # Обработка ошибки отправки
            print(f"Ошибка отправки в Telegram: {response.text}")
        # Можно перенаправить на страницу с ошибкой или показать уведомление
    return render(request, 'main/payment.html', {
           'product': selected_product
        })


def final_page(request, product_category, product_slug):
    # Проверяем, есть ли флаг в сессии
    if not request.session.get('purchase_successful'):
        return redirect('/')  # Перенаправляем на главную или другую страницу, если доступа нет
    
    # Удаляем флаг после первого посещения
    del request.session['purchase_successful']
    return render(request, 'main/final.html')


def product_details(request, product_slug, product_category):
    try:
        selected_product = SortedProducts.objects.get(slug=product_slug, category__category=product_category)
        return render(request, 'main/product_details.html', {
           'product': selected_product
        })

    except Exception as exc:
        return render(request, 'main/product_details.html',{
        })


# Includes Category model
from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max
from .models import SortedProducts, Category, Brand

def products_list(request, product_category):
    selected_category = get_object_or_404(Category, category=product_category)
    sorted_products = SortedProducts.objects.filter(category=selected_category).order_by('-price')

    # Получаем параметры фильтрации из запроса
    query = request.GET.get('q')
    fps_filter = request.GET.getlist('fps')
    brand_filter = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    switch_type_filter = request.GET.getlist('switch_type')
    backlight_filter = request.GET.getlist('backlight')
    dpi_filter = request.GET.getlist('dpi')
    sensor_type_filter = request.GET.getlist('sensor_type')
    socket_type_filter = request.GET.getlist('socket_type')
    form_factor_filter = request.GET.getlist('form_factor')
    ram_type_filter = request.GET.getlist('ram_type')
    ram_size_filter = request.GET.getlist('ram_size')
    power_wattage_filter = request.GET.getlist('power_wattage')
    certification_filter = request.GET.getlist('certification')
    storage_type_filter = request.GET.getlist('storage_type')
    storage_size_filter = request.GET.getlist('storage_size')
    cooling_type_filter = request.GET.getlist('cooling_type')
    video_memory_filter = request.GET.getlist('video_memory')
    connection_type_filter = request.GET.getlist('connection_type')
    mouse_pad_size_filter = request.GET.getlist('mouse_pad_size')

    # Применяем поиск по заголовку, если он предоставлен
    if query:
        sorted_products = sorted_products.filter(title__icontains=query)

    # Применяем фильтры в зависимости от категории
    if selected_category.category.lower() == 'monitor':
        if fps_filter and '' not in fps_filter:
            sorted_products = sorted_products.filter(fps__in=fps_filter)

    if selected_category.category.lower() == 'keyboard':
        if switch_type_filter and '' not in switch_type_filter:
            sorted_products = sorted_products.filter(switch_type__in=switch_type_filter)
        if backlight_filter and '' not in backlight_filter:
            sorted_products = sorted_products.filter(backlight__in=backlight_filter)
        
    if selected_category.category.lower() == 'cooling':
        if cooling_type_filter and '' not in cooling_type_filter:
            sorted_products = sorted_products.filter(cooling_type__in=cooling_type_filter)

    if selected_category.category.lower() == 'mouse':
        if dpi_filter and '' not in dpi_filter:
            sorted_products = sorted_products.filter(dpi__in=dpi_filter)
        if sensor_type_filter and '' not in sensor_type_filter:
            sorted_products = sorted_products.filter(sensor_type__in=sensor_type_filter)

    if selected_category.category.lower() == 'motherboard':
        if socket_type_filter and '' not in socket_type_filter:
            sorted_products = sorted_products.filter(socket_type__in=socket_type_filter)
        if form_factor_filter and '' not in form_factor_filter:
            sorted_products = sorted_products.filter(form_factor__in=form_factor_filter)

    if selected_category.category.lower() == 'ram':
        if ram_type_filter and '' not in ram_type_filter:
            sorted_products = sorted_products.filter(ram_type__in=ram_type_filter)
        if ram_size_filter and '' not in ram_size_filter:
            sorted_products = sorted_products.filter(ram_size__in=ram_size_filter)

    if selected_category.category.lower() == 'power-supply':
        if power_wattage_filter and '' not in power_wattage_filter:
            sorted_products = sorted_products.filter(power_wattage__in=power_wattage_filter)
        if certification_filter and '' not in certification_filter:
            sorted_products = sorted_products.filter(certification__in=certification_filter)

    if selected_category.category.lower() == 'storage':
        if storage_type_filter and '' not in storage_type_filter:
            sorted_products = sorted_products.filter(storage_type__in=storage_type_filter)
        if storage_size_filter and '' not in storage_size_filter:
            sorted_products = sorted_products.filter(storage_size__in=storage_size_filter)

    if selected_category.category.lower() == 'graphics-card':
        if video_memory_filter and '' not in video_memory_filter:
            sorted_products = sorted_products.filter(video_memory__in=video_memory_filter)

    if selected_category.category.lower() == 'headphones':
        if connection_type_filter and '' not in connection_type_filter:
            sorted_products = sorted_products.filter(connection_type__in=connection_type_filter)

    if selected_category.category.lower() == 'mouse-pad':
        if mouse_pad_size_filter and '' not in mouse_pad_size_filter:
            sorted_products = sorted_products.filter(mouse_pad_size__in=mouse_pad_size_filter)

    if selected_category.category.lower() == 'case':
        if form_factor_filter and '' not in form_factor_filter:
            sorted_products = sorted_products.filter(form_factor__in=form_factor_filter)

    # Применяем фильтр бренда, если он предоставлен и не пустой
    if brand_filter and '' not in brand_filter:
        sorted_products = sorted_products.filter(brand__in=brand_filter)

    # Применяем фильтр по диапазону цен, если они предоставлены
    if min_price:
        try:
            sorted_products = sorted_products.filter(price__gte=float(min_price))
        except ValueError:
            pass  # Игнорируем ошибки конвертации
    if max_price:
        try:
            sorted_products = sorted_products.filter(price__lte=float(max_price))
        except ValueError:
            pass  # Игнорируем ошибки конвертации

    # Получаем доступные бренды и опции фильтров для выбранной категории
    brands = Brand.objects.filter(sortedproducts__category=selected_category).distinct()
    fps_options = sorted(filter(None, set(sorted_products.values_list('fps', flat=True))))
    switch_type_options = sorted(filter(None, set(sorted_products.values_list('switch_type', flat=True))))
    backlight_options = sorted(filter(None, set(sorted_products.values_list('backlight', flat=True))))
    dpi_options = sorted(filter(None, set(sorted_products.values_list('dpi', flat=True))))
    sensor_type_options = sorted(filter(None, set(sorted_products.values_list('sensor_type', flat=True))))
    socket_type_options = sorted(filter(None, set(sorted_products.values_list('socket_type', flat=True))))
    form_factor_options = sorted(filter(None, set(sorted_products.values_list('form_factor', flat=True))))
    ram_type_options = sorted(filter(None, set(sorted_products.values_list('ram_type', flat=True))))
    ram_size_options = sorted(filter(None, set(sorted_products.values_list('ram_size', flat=True))))
    power_wattage_options = sorted(filter(None, set(sorted_products.values_list('power_wattage', flat=True))))
    certification_options = sorted(filter(None, set(sorted_products.values_list('certification', flat=True))))
    storage_type_options = sorted(filter(None, set(sorted_products.values_list('storage_type', flat=True))))
    storage_size_options = sorted(filter(None, set(sorted_products.values_list('storage_size', flat=True))))
    cooling_type_options = sorted(filter(None, set(sorted_products.values_list('cooling_type', flat=True))))
    video_memory_options = sorted(filter(None, set(sorted_products.values_list('video_memory', flat=True))))
    connection_type_options = sorted(filter(None, set(sorted_products.values_list('connection_type', flat=True))))
    mouse_pad_size_options = sorted(filter(None, set(sorted_products.values_list('mouse_pad_size', flat=True))))

    # Получаем минимальные и максимальные цены для выбранной категории
    price_range = SortedProducts.objects.filter(category=selected_category).aggregate(
        Min('price'), Max('price')
    )
    min_price_db = price_range['price__min'] or 0
    max_price_db = price_range['price__max'] or 0

    no_products_found = not sorted_products.exists()  # Проверяем наличие товаров

    return render(request, 'main/products_list.html', {
        'sorted_products': sorted_products,
        'selected_category': selected_category,
        'search_query': query,
        'fps_filter': fps_filter,
        'brand_filter': brand_filter,
        'min_price': min_price or min_price_db,
        'max_price': max_price or max_price_db,
        'brands': brands,
        'fps_options': fps_options,
        'switch_type_options': switch_type_options,
        'backlight_options': backlight_options,
        'dpi_options': dpi_options,
        'sensor_type_options': sensor_type_options,
        'socket_type_options': socket_type_options,
        'form_factor_options': form_factor_options,
        'ram_type_options': ram_type_options,
        'ram_size_options': ram_size_options,
        'power_wattage_options': power_wattage_options,
        'certification_options': certification_options,
        'storage_type_options': storage_type_options,
        'storage_size_options': storage_size_options,
        'cooling_type_options': cooling_type_options,
        'video_memory_options': video_memory_options,
        'connection_type_options': connection_type_options,
        'mouse_pad_size_options': mouse_pad_size_options,
        'no_products_found': no_products_found,
    })

def search(request):
    query = request.GET.get('q')

    if query:
        # Convert the query to a slug for exact matching
        product_slug = slugify(query)

        # First, attempt to find a specific product by slug
        try:
            product = SortedProducts.objects.get(slug=product_slug)
            category_name = product.category.category  # Get the category name
            
            # Redirect to the product detail page if found
            return redirect('product-detail', product_category=category_name, product_slug=product_slug)

        except SortedProducts.DoesNotExist:
            # If the specific product is not found, search for products containing the query in title or slug
            products = SortedProducts.objects.filter(title__icontains=query) | SortedProducts.objects.filter(slug__icontains=query)

            # Get all brand names
            all_brands = Brand.objects.all().values_list('brand', flat=True)

            # Find close matches for the query in brands
            matched_brands = process.extract(query, all_brands, limit=4)  # Get top 5 close matches
            close_brand_names = [brand for brand, score in matched_brands if score >= 70]  # Threshold score for matches

            # Also filter products by close brand names if there are any
            if close_brand_names:
                products |= SortedProducts.objects.filter(brand__brand__in=close_brand_names)

            if products.exists():
                # Render results if products are found
                return render(request, 'main/found_products.html', {
                    'sorted_products': products,
                    'query': query,
                })
            else:
                return render(request, 'main/no_found.html', {
                    'sorted_products': [],
                    'error': 'No products found matching your search.'
                })
    else:
        # Handle the case where no query is provided
        return render(request, 'main/no_found.html', {
            'sorted_products': [],
            'error': 'No search query provided.'
        })