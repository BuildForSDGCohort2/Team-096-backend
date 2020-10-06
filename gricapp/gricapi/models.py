"""
Models for GricApp
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from .managers import CustomUserManager
from django.template.defaultfilters import slugify
from django.utils import timezone
from uuid import uuid4
from django.contrib.auth.models import Group


class UUIDModel(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid4, editable=False, unique=True)


class User(AbstractUser):
    groups = models.ForeignKey(
        Group, on_delete=models.CASCADE)
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        if self.first_name != "":
            return "{}".format(self.first_name.capitalize())
        return "{}".format(self.email)


class Profile(models.Model):
    GENDER = (
        (None, 'Select gender'),
        ('M', 'Male'),
        ('F', 'Female')
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    is_farmer = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)

    def __str__(self):
        if self.is_farmer:
            return "{} is a farmer".format(self.user)
        return "{}".format(self.user)


class Category(models.Model):
    """ Category of produce """
    category_name = models.CharField(
        max_length=200, db_index=True, default="General")
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=['category_name', 'slug'],
                name='name_slug_unique')
        ]

    def __str__(self):
        return self.category_name

    # pylint: disable=arguments-differ,signature-differs
    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if not self.slug:
            strftime = "".join(str(timezone.now()).split("."))
            new_string = "%s-cat-%s" % (self.category_name, strftime[11:-3])
            self.slug = slugify(new_string)
        elif "cat" not in self.slug:
            strftime = "".join(str(timezone.now()).split("."))
            new_string = "%s-cat-%s" % (self.category_name, strftime[11:-3])
            self.slug = slugify(new_string)


class Produce(models.Model):
    """ Model for Produce """

    MEASUREMENT_UNITS = (
        ('Bags', 'bags'),
        ('Tonnes', 'tonnes'),
        ('Single units(Retail)', 'units')
    )

    produce_name = models.CharField(max_length=150, blank=False)
    produce_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    slug = models.SlugField(max_length=200, db_index=True)
    stock = models.PositiveIntegerField(blank=True, default=0)
    measurement_unit = models.CharField(max_length=25, default="bags",
                                        choices=MEASUREMENT_UNITS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="produces", on_delete=models.CASCADE)
    price_tag = models.DecimalField(
        max_digits=10, default=0.00, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('api:products-detail', args=[str(self.id)])

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return self.produce_name

    # pylint: disable=arguments-differ,signature-differs
    def save(self, *args, **kwargs):
        super(Produce, self).save(*args, **kwargs)
        if not self.slug:
            strftime = "".join(str(timezone.now()).split("."))
            new_string = "%s-pro-%s" % (self.produce_name, strftime[11:-3])
            self.slug = slugify(new_string)
        elif "pro" not in self.slug:
            strftime = "".join(str(timezone.now()).split("."))
            new_string = "%s-pro-%s" % (self.produce_name, strftime[11:-3])
            self.slug = slugify(new_string)


class Order(UUIDModel):
    transaction_date = models.DateTimeField(auto_now_add=True)
    update_transaction_date = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    consumer = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.CASCADE
    )
    order_status = models.CharField(max_length=26, default="pending")

    def __str__(self):
        return "{}".format(self.id)

    @property
    def total_cost(self):
        cost = sum(item.price for item in self.items.all())
        return cost


class OrderItem(models.Model):
    item_id = models.UUIDField(default=uuid4, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey(
        Produce, on_delete=models.CASCADE, related_name="order_items")
    quantity_ordered = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        default="pending", max_length=30)

    def __str__(self):
        return "Item{}".format(self.item_id)

    # pylint: disable=arguments-differ,signature-differs
    def save(self, *args, **kwargs):
        self.price = self.quantity_ordered * self.produce.price_tag
        super(OrderItem, self).save(*args, **kwargs)
