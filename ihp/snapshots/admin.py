from django.contrib import admin
from models import Case, CaseRun, Version


class CaseAdmin(admin.ModelAdmin):
    list_filter = ("agency", "country", "indicator", "calc_function")
    list_display = ("name", "agency", "country", "indicator", "calc_function")

admin.site.register(Case, CaseAdmin)


class CaseRunAdmin(admin. ModelAdmin):
    list_filter = ("version",)
    list_display = ("case", "version", "base_val", "base_year", "cur_val",
                    "cur_year")

admin.site.register(CaseRun, CaseRunAdmin)


class VersionAdmin(admin.ModelAdmin):
    list_display = ("description", "creation")

admin.site.register(Version, VersionAdmin)
