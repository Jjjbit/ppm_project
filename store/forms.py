from django import forms
from .models import Product, Category
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'discount',
            'image',
            'stock',
            'category',
            'description',
        ]

        def clean_image(self):
            image = self.cleaned_data.get('image')
            if image:
                img = Image.open(image)
                width, height = img.size
                aspect_ratio = width / height if height != 0 else 0

                if width < 400 or height < 400:
                    raise ValidationError("Image size must be at least 400x400")

                if not (0.5 <= aspect_ratio <= 2):
                    raise ValidationError("Image aspect ratio must be between 0.5 and 2")

            return image

        def clean_discount(self):
            discount = self.cleaned_data.get("discount")
            price = self.cleaned_data.get("price")

            if discount is not None and discount >= 0:
                raise forms.ValidationError("Discount must be negative")

            return discount

