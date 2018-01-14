from django.contrib import admin

# Register your models here.
from .models import Person, Hit, HitCount

########
#Person#
########

class PersonAdmin(admin.ModelAdmin):
	list_display = ["username","first","last","isreal"]
	search_fields = ["username"]


##########################################

admin.site.register(Person,PersonAdmin)
admin.site.register(Hit)
admin.site.register(HitCount)