# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
    search_fields = ['last_name']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            for contract in obj.contract_set.all():
                contract.credits_set.all().delete()
                contract.creditshistory_set.all().delete()
                contract.delete()
            obj.delete()
    delete_selected.short_description = u"УДАЛЕНИЕ С ПЛАТЕЖАМИ И ДОЛГАМИ"


admin.site.register(Client, ClientAdmin)
