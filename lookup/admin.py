from django.contrib import admin

# Register your models here.
from .models import Person, Hit, HitCount, Query

########
#Person#
########

class PersonAdmin(admin.ModelAdmin):
	list_display = ["username","first","last","isreal"]
	search_fields = ["username"]

######
#Hits#
######

class HitAdmin(admin.ModelAdmin):
	list_display = ["source","target","valid"]
	search_fields = ["source"]

class HitCountAdmin(admin.ModelAdmin):
	list_display = ["username","count"]
	search_fields = ["username"]

############
#Query logs#
############

class QueryAdmin(admin.ModelAdmin):
	list_display = ["qdate","query","nrecords"]

##########################################

admin.site.register(Person,PersonAdmin)
admin.site.register(Hit,HitAdmin)
admin.site.register(HitCount,HitCountAdmin)
admin.site.register(Query,QueryAdmin)