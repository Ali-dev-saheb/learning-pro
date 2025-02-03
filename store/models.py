from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True, null=True)

    # Pricing
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Stock & Availability
    stock = models.PositiveIntegerField(default=0)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def clean(self):
        """Ensure only one of the fields (image or image_url) is provided, but don't auto-remove either."""
        if self.image and self.image_url:
            raise ValidationError("You cannot provide both an image and an image URL. Choose one.")
        if not self.image and not self.image_url:
            raise ValidationError("You must provide either an image or an image URL.")

    def get_image(self):
        """Return the correct image source (uploaded file or external URL)."""
        return self.image.url if self.image else self.image_url if self.image_url else None

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
