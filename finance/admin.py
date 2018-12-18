from django.contrib import admin

from .models import Goods, CreditsHistory


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'goods_type')
    list_filter = ('is_active', 'goods_type')
    actions = ['make_active', 'make_deactive']
    readonly_fields = [x.name for x in Goods._meta.fields]

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Activate"

    def make_deactive(self, request, queryset):
        queryset.update(is_active=False)
    make_deactive.short_description = "Deactivate"


class CreditsHistoryAdmin(admin.ModelAdmin):
    readonly_fields = [x.name for x in CreditsHistory._meta.fields]


admin.site.register(Goods, GoodsAdmin)
admin.site.register(CreditsHistory, CreditsHistoryAdmin)
