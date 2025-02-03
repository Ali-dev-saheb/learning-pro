from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'store/product_list.html', {'products': products})
