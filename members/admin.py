from django import forms
from django.contrib import admin

from members.models import Member
from members.models import Parent
from members.models import Phone
from members.models import Address
from members.models import Belt
from members.models import Tournament
from members.models import Membership_fee
from members.models import USJF_membership
from members.models import Last_modify_ip
from members.models import Announce
from members.models import Notification


class BeltInline(admin.TabularInline):
    model = Belt
    extra = 1

class USJF_MembershipInline(admin.TabularInline):
    model = USJF_membership
    extra = 1
    
class LastModifyIpInline(admin.TabularInline):
    model = Last_modify_ip
    extra = 1

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1

class FeeInline(admin.TabularInline):
    model = Membership_fee
    extra = 1

class TournamentInline(admin.TabularInline):
    model = Tournament
    extra = 1

class MemberPhoneInline(admin.TabularInline):
    model = Phone
    extra = 1

class ParentInline(admin.StackedInline):
    model = Parent
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Information',      {'fields': ['avatar_img', 'first_name', 'last_name', 'gender', 'birthday', 'emergency_number', 'email', 'joined_date', 'grade' ]}),
        ('Still attending?',          {'fields': ['activation']})
    ]
    inlines = [AddressInline, MemberPhoneInline, BeltInline, ParentInline, USJF_MembershipInline, FeeInline, TournamentInline, LastModifyIpInline]

class AnnounceAdmin(admin.ModelAdmin):
    list_display = ('subject', 'pub_date')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('event', 'days', 'repetitive')

admin.site.register(Member, MemberAdmin)
admin.site.register(Announce, AnnounceAdmin)
admin.site.register(Notification, NotificationAdmin)
