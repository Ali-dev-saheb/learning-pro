from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
import csv
from django.contrib import messages
from io import TextIOWrapper
from .models import Product, Category, ProductImage, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1  

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'stock', 'created_at', 'display_all_images')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_at')
    fields = ('name', 'category', 'description', 'mrp', 'selling_price', 'stock', 'created_at')
    readonly_fields = ('created_at',)
    inlines = [ProductImageInline, ReviewInline]
    change_list_template = "admin/csv_upload_list.html"  # Ensure this template exists

    def display_all_images(self, obj):
        images = obj.product_images.all()
        if images:
            return format_html(" ".join([
                f'<img src="{img.image.url}" width="50" height="50" style="margin:2px;">' 
                for img in images
            ]))
        return "No images"
    display_all_images.short_description = 'Images'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='product_upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file!')
                return redirect("..")

            data = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(data)

            for row in reader:
                category, _ = Category.objects.get_or_create(name=row["category"].strip())
                product = Product.objects.create(
                    name=row["name"].strip(),
                    category=category,
                    description=row.get("description", ""),
                    mrp=row["mrp"],
                    selling_price=row["selling_price"],
                    stock=row["stock"],
                )

                image_url = row.get("image_url", "").strip()
                if image_url:
                    ProductImage.objects.create(product=product, image_url=image_url)

            messages.success(request, 'CSV file uploaded successfully!')
            return redirect("..")

        return render(request, "admin/upload_csv.html", {})

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Review)
