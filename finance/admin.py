from django.contrib import admin

from .models import Goods


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'goods_type')
    list_filter = ('is_active', 'goods_type')
    actions = ['make_active', 'make_deactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Activate"

    def make_deactive(self, request, queryset):
        queryset.update(is_active=False)
    make_deactive.short_description = "Deactivate"


admin.site.register(Goods, GoodsAdmin)
