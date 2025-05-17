from django.contrib import admin

from events.models import BaseEvent, UserEvent, UserNetwork
# Register your models here.

admin.site.register(UserNetwork)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ['id','title']


admin.site.register(UserEvent,UserEventAdmin)

admin.site.register(BaseEvent)



