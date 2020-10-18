# Register your models here.
from django.contrib import admin
from gricapi.models import (
    User, Profile, Produce, Order, OrderItem, Category
)


class ProfileInline(admin.TabularInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'date_joined')
    inlines = [ProfileInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    prepopulated_fields = {'slug': ('category_name',)}


class ProduceAdmin(admin.ModelAdmin):
    list_display = ('produce_name', 'produce_category', 'slug',
                    'price_tag', 'stock', 'measurement_unit',
                    'image_url', 'product_description', 'owner',
                    'date_modified')
    list_filter = ('produce_category', 'stock', 'date_modified',
                   'owner')
    list_editable = ('price_tag', 'stock')
    prepopulated_fields = {'slug': ('produce_name',)}


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_status', 'transaction_date',
                    'update_transaction_date', 'paid',
                    'consumer', 'paid')


admin.site.register(User, UserAdmin)
admin.site.register(Produce, ProduceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category, CategoryAdmin)
