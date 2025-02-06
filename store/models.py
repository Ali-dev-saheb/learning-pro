import csv
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.base import ContentFile
import requests

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Optional SKU
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Optional Image URL

    def __str__(self):
        return f"{self.product.name} - {self.size or ''} {self.color or ''} ({self.sku or 'No SKU'})"

class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def clean(self):
        """Ensure only one of the fields (image or image_url) is provided."""
        if self.image and self.image_url:
            raise ValidationError("You cannot provide both an image and an image URL. Choose one.")
        if not self.image and not self.image_url:
            raise ValidationError("You must provide either an image or an image URL.")

    def display_image(self):
        """Return an image tag for displaying images in Django Admin."""
        if self.image_url:
            return format_html('<img src="{}" width="50" height="50" style="margin:2px;">', self.image_url)
        elif self.image:
            return format_html('<img src="{}" width="50" height="50" style="margin:2px;">', self.image.url)
        return "No image"

    display_image.short_description = "Image"

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating}/5"
