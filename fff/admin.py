from fff.models import Host, Control, Area, User, TimeSlot, ProductionEnvironment, ControlStatus, ExecutedControl, FileServe, Statistic
from fff.models import StatType
from django.contrib import admin



class ControlPEInline(admin.TabularInline):
    model = Control.productionEnvironment.through
    verbose_name = "Controllo"
    verbose_name_plural = "Controlli definiti"

class StatisticAdmin(admin.ModelAdmin):
    list_display = ('stat_element','productionEnvironment','statType','stat_time','timestamp','stat_value','stat_extra')
    list_filter = ('statType','stat_time','productionEnvironment__name')
    search_fields = ('stat_element',)

class StatTypeAdmin(admin.ModelAdmin):
    '''statistic admin class for Error statistics'''

class ControlAdmin(admin.ModelAdmin):
    inlines = [
        ControlPEInline,
    ]
    exclude = ('productionEnvironment',)

class HostAdmin(admin.ModelAdmin):
    list_display = ('name','ip',)

class AreaAdmin(admin.ModelAdmin):
    list_display = ('name','productionEnvironment')

class UserAdmin(admin.ModelAdmin):
    list_display = ('name',)

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time',)

class ProductionEnvironmentAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    search_fields = ('name',)
    inlines = [
        ControlPEInline,
    ]

class ControlStatusAdmin(admin.ModelAdmin):
    list_display = ('control',)

class ExecutedControlAdmin(admin.ModelAdmin):
    list_display = ('control','control_time',)

class FileServeAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'productionEnvironment', 'destination_path', 'permissions', 'error')


admin.site.register(Statistic, StatisticAdmin)
admin.site.register(StatType, StatTypeAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Control, ControlAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ProductionEnvironment, ProductionEnvironmentAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(ControlStatus, ControlStatusAdmin)
admin.site.register(ExecutedControl, ExecutedControlAdmin)
admin.site.register(FileServe, FileServeAdmin)
