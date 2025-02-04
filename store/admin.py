from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
import csv
from django.contrib import messages
from io import TextIOWrapper
import requests
from django.core.files.base import ContentFile
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
            return format_html(" ".join([f'<img src="{img.image_url}" width="50" height="50" style="margin:2px;">' for img in images if img.image_url]))
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

            try:
                ProductCSVUploadHandler.handle_bulk_upload(csv_file)
                messages.success(request, 'CSV file uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error processing CSV: {e}")

            return redirect("..")

        return render(request, "admin/upload_csv.html", {})

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('product_images')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(ProductImage)  # Now visible in Django Admin


class ProductCSVUploadHandler:
    @staticmethod
    def handle_bulk_upload(csv_file):
        """
        Handles bulk upload of products with multiple images stored in separate columns.
        """
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

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

            # Process all columns dynamically that contain 'image_url'
            for key, image_url in row.items():
                if key.startswith("image_url") and image_url.strip():
                    ProductImage.objects.create(product=product, image_url=image_url.strip())

