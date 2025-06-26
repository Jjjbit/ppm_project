from .models import Product, Category, ReturnRequest, StoreCategory, Store
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
import os

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class StoreCategoryForm(forms.ModelForm):
    class Meta:
        model = StoreCategory
        fields = ['name']
        labels= {'name': 'Category Name'}

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            store = Store.objects.filter(owner=user).first()
            if store:
                self.fields['store_category'].queryset = StoreCategory.objects.filter(store=store)
            else:
                self.fields['store_category'].queryset = StoreCategory.objects.none()

    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'discount',
            'image',
            'stock',
            'category',
            'store_category',
            'description',
        ]

        def clean_image(self):
            image = self.cleaned_data.get('image')
            if image:
                img = Image.open(image)
                img = img.convert('RGB')

                width, height = img.size
                min_side = min(width, height)
                left = (width - min_side) // 2
                top = (height - min_side) // 2
                right = (width + min_side)
                bottom = (height + min_side)
                img = img.crop((left, top, right, bottom))

                img = img.resize((400, 400), Image.Resampling.LANCZOS)

                buffer = BytesIO()
                img.save(fp=buffer, format='JPEG')

                filename = os.path.splitext(image.name)[0]
                new_filename = f"{filename}_cropped.jpg"

                self.cleaned_data['image'] = ContentFile(buffer.read(), name=new_filename)


            return self.cleaned_data['image']


        def clean_discount(self):
            discount = self.cleaned_data.get("discount")

            if discount is not None and discount >= 0:
                raise forms.ValidationError("Discount must be negative")
            return discount

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Explain why you want to return this item...'}),
        }