
from django.contrib import admin
from .models import Store, Bills, Users


# Admin panel branding
admin.site.site_header = "StockFlow Administration"
admin.site.site_title = "StockFlow Admin"
admin.site.index_title = "Store Management Dashboard"


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):

    list_display = (
        'p_id',
        'p_name',
        'p_price',
        'p_quantity',
        'p_list_date',
        'user',
    )

    list_display_links = ('p_id', 'p_name')

    search_fields = ('p_name', '=p_id')

    list_filter = ('p_list_date', 'user')

    ordering = ('-p_list_date',)

    list_per_page = 25

    date_hierarchy = 'p_list_date'

    list_select_related = ('user',)


@admin.register(Bills)
class BillsAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'customer_mobile',
        'purchase_product',
        'quantity',
        'bill_date',
        'user',
    )

    list_display_links = ('id', 'customer_name')

    search_fields = (
        'customer_name',
        'customer_mobile',
        '=purchase_product',
    )

    list_filter = ('bill_date', 'user')

    ordering = ('-bill_date',)

    list_per_page = 25

    date_hierarchy = 'bill_date'

    list_select_related = ('user',)


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user_name',
        'user_mobile',
        'store_name',
        'user_created_at',
    )

    list_display_links = ('id', 'user_name')

    search_fields = (
        'user_name',
        'user_mobile',
        'store_name',
    )

    list_filter = ('user_created_at',)

    ordering = ('-user_created_at',)

    list_per_page = 25

    date_hierarchy = 'user_created_at'