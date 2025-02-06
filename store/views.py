from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.prefetch_related('product_images', 'variants').all()
    return render(request, 'store/product_list.html', {'products': products})
