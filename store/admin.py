from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
import csv
from django.contrib import messages
from io import TextIOWrapper
import requests
from django.core.files.base import ContentFile
from .models import Product, Category, ProductImage, Review, ProductVariant

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1  

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  
    fields = ('sku', 'size', 'color', 'selling_price', 'stock', 'image_url', 'display_variant_image')
    readonly_fields = ('display_variant_image',)

    def display_variant_image(self, obj):
        if obj.image_url:
            return format_html(f'<img src="{obj.image_url}" width="50" height="50" style="margin:2px;">')
        return "No image"

    display_variant_image.short_description = 'Variant Image'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'stock', 'created_at', 'display_all_images')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_at')
    fields = ('name', 'category', 'description', 'mrp', 'selling_price', 'stock', 'created_at')
    readonly_fields = ('created_at',)
    inlines = [ProductImageInline, ReviewInline, ProductVariantInline]  # ✅ Added Variants Inline
    change_list_template = "admin/csv_upload_list.html"  # Ensure this template exists

    def display_all_images(self, obj):
        """
        Show images from both ProductImage and ProductVariant in the Product admin panel.
        """
        # Get all product images
        product_images = obj.product_images.all()

        # Get all variant images
        variant_images = obj.variants.all()

        # Combine images from ProductImage and ProductVariant
        all_images = []

        for img in product_images:
            if img.image_url:
                all_images.append(f'<img src="{img.image_url}" width="50" height="50" style="margin:2px;">')

        for variant in variant_images:
            if variant.image_url:
                all_images.append(f'<img src="{variant.image_url}" width="50" height="50" style="margin:2px;">')

        # Display images if available
        if all_images:
            return format_html(" ".join(all_images))
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
admin.site.register(ProductVariant)  # ✅ Registered in Admin


class ProductCSVUploadHandler:
    @staticmethod
    def handle_bulk_upload(csv_file):
        """
        Handles bulk upload of products and variants from a CSV file.
        """
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            # Get or create category
            category_name = row.get("category", "").strip()
            if category_name:
                category, _ = Category.objects.get_or_create(name=category_name)
            else:
                category = None  # Allow product without a category

            # Get or create product
            product, _ = Product.objects.get_or_create(
                name=row.get("product_name", "").strip(),
                category=category,
                defaults={
                    "description": row.get("description", "").strip(),
                    "mrp": row.get("mrp") or None,
                    "selling_price": row.get("selling_price") or None,
                    "stock": row.get("stock") or 0,
                }
            )

            # Create variant if SKU or size/color is provided
            sku = row.get("sku", "").strip()
            size = row.get("size", "").strip()
            color = row.get("color", "").strip()
            if sku or size or color:  # Only create variant if any of these are present
                ProductVariant.objects.create(
                    product=product,
                    sku=sku or None,
                    size=size or None,
                    color=color or None,
                    selling_price=row.get("selling_price") or None,
                    stock=row.get("stock") or 0,
                    image_url=row.get("image_url", "").strip() or None,
                )
