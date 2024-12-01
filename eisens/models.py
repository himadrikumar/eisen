from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

"""class Page(models.Model):
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.date_created.strftime('%Y-%m-%d')"""

class Category(models.Model):
    # page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# Signal to create default categories when a page is created
"""@receiver(post_save, sender=Page)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        # Create four default categories for each new page
        default_category_names = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
        for name in default_category_names:
            Category.objects.create(page=instance, name=name)
"""