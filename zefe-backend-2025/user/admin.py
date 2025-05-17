from django.contrib import admin

from user.models import User, UserProfile,Position,Field,UserField,UserFeedback
# Register your models here.


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Position)
admin.site.register(Field)
admin.site.register(UserField)
admin.site.register(UserFeedback)
