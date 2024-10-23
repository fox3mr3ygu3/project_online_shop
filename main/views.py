from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, SortedProducts, Category, Brand, VisitorCounter
from django.utils.text import slugify
from django.db.models import Min, Max, F
from django.http import JsonResponse
from fuzzywuzzy import process
from django.utils import timezone
from datetime import timedelta



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


def buy(request):
    return render(request, 'main/payment.html')


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
def products_list(request, product_category):
    selected_category = get_object_or_404(Category, category=product_category)
    sorted_products = SortedProducts.objects.filter(category=selected_category).order_by('-price')

    # Получаем параметры фильтрации из запроса
    query = request.GET.get('q')
    fps_filter = request.GET.getlist('fps')  # Ожидаем список для множественного выбора
    brand_filter = request.GET.getlist('brand')  # Ожидаем список для множественного выбора
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Применяем поиск по заголовку, если он предоставлен
    if query:
        sorted_products = sorted_products.filter(title__icontains=query)

    # Применяем фильтр FPS, если он предоставлен и не пустой
    if fps_filter and any(fps_filter):
        sorted_products = sorted_products.filter(fps__in=fps_filter)

    # Применяем фильтр бренда, если он предоставлен и не пустой
    if brand_filter and any(brand_filter):
        sorted_products = sorted_products.filter(brand__in=brand_filter)

    # Применяем фильтр по диапазону цен, если они предоставлены
    if min_price:
        try:
            sorted_products = sorted_products.filter(price__gte=float(min_price))  # Используем только price
        except ValueError:
            pass  # Игнорируем ошибки конвертации
    if max_price:
        try:
            sorted_products = sorted_products.filter(price__lte=float(max_price))  # Используем только price
        except ValueError:
            pass  # Игнорируем ошибки конвертации

    # Получаем доступные бренды и FPS для выбранной категории
    brands = Brand.objects.filter(sortedproducts__category=selected_category).distinct()
    fps_options = sorted_products.values_list('fps', flat=True).distinct()
    
    # Получаем минимальные и максимальные цены для выбранной категории
    price_range = SortedProducts.objects.filter(category=selected_category).aggregate(
        Min('price'), Max('price')  # Исправлено: убираем _amount
    )
    min_price_db = price_range['price__min'] or 0
    max_price_db = price_range['price__max'] or 0

    no_products_found = not sorted_products.exists()  # Проверяем наличие товаров

    return render(request, 'main/products_list.html', {
        'sorted_products': sorted_products,
        'selected_category': selected_category,
        'search_query': query,  # Передаём запрос поиска обратно в шаблон
        'fps_filter': fps_filter,  # Передаём выбранный фильтр FPS
        'brand_filter': brand_filter,  # Передаём выбранный фильтр бренда
        'min_price': min_price or min_price_db,  # Передаём фильтр минимальной цены
        'max_price': max_price or max_price_db,  # Передаём фильтр максимальной цены
        'brands': brands,  # Передаём доступные бренды
        'fps_options': fps_options,  # Передаём доступные FPS
        'no_products_found': no_products_found,  # Передаём флаг отсутствия товаров
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
        return render(request, 'main/no_found.html', {
            'sorted_products': [],
            'error': 'No search query provided.'
        })