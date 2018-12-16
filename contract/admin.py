from django.contrib import admin

from .models import Contract, PeriodTimeType, PeriodTime


class PeriodTimeInline(admin.TabularInline):
    model = PeriodTime


class PeriodTimeTypeAdmin(admin.ModelAdmin):
    inlines = [
        PeriodTimeInline,
    ]


admin.site.register(PeriodTimeType, PeriodTimeTypeAdmin)
admin.site.register(Contract)
