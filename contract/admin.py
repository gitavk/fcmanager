# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Contract, PeriodTimeType, PeriodTime


class PeriodTimeInline(admin.TabularInline):
    model = PeriodTime


class PeriodTimeTypeAdmin(admin.ModelAdmin):
    inlines = [
        PeriodTimeInline,
    ]


class ContractAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
    search_fields = ['number']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            obj.credits_set.all().delete()
            obj.creditshistory_set.all().delete()
            obj.delete()
    delete_selected.short_description = u"УДАЛЕНИЕ С ПЛАТЕЖАМИ И ДОЛГАМИ"


admin.site.register(PeriodTimeType, PeriodTimeTypeAdmin)
admin.site.register(Contract, ContractAdmin)
