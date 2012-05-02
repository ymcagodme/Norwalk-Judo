from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField
from django.contrib import admin

from members.models import Member
from members.models import Parent
from members.models import Phone
from members.models import Address
from members.models import Belt
from members.models import Tournament
from members.models import Membership_fee
from members.models import USJF_membership
from members.models import Announce
from members.models import Notification
from members.models import Last_modify_ip


class BeltInline(admin.TabularInline):
    model = Belt
    extra = 1

class USJF_MembershipInline(admin.TabularInline):
    model = USJF_membership
    extra = 1

class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['postal'] = USZipCodeField()

class AddressInline(admin.TabularInline):
    model = Address
    form = AddressForm
    extra = 1

class FeeInline(admin.TabularInline):
    model = Membership_fee
    extra = 1

class TournamentInline(admin.TabularInline):
    model = Tournament
    extra = 1

class MemberPhoneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MemberPhoneForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'] = USPhoneNumberField()

class MemberPhoneInline(admin.TabularInline):
    model = Phone
    form = MemberPhoneForm
    extra = 1

class ParentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParentForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'] = USPhoneNumberField()

class ParentInline(admin.StackedInline):
    model = Parent
    form = ParentForm
    extra = 1

class LastModifyInline(admin.StackedInline):
    model = Last_modify_ip
    extra = 1

class MemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['emergency_number'] = USPhoneNumberField()

class MemberAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        IP_ADDR = request.META['REMOTE_ADDR']
        if change:
            obj.last_modify_ip_set.create(ip=IP_ADDR)
        else:
            obj.save() # need to save first, otherwise cannot assign the foreign key
            ip_obj = Last_modify_ip.objects.create(member=obj)
            ip_obj.ip = IP_ADDR
            ip_obj.save()
        obj.save()

    def gen_qrcode(self, obj):
        data = 'http://norwalkjudo.appsopt.com/members/%i/' % (obj.pk, )
        size = 200
        error_corrction = 'L'
        url = 'https://chart.googleapis.com/chart?cht=qr&chs=%ix%i&chl=%s&chld=%s|0' % (size, size, data, error_corrction)
        return '<img src=%s />' % url
    gen_qrcode.allow_tags = True
    gen_qrcode.short_description = 'QR Code'

    form = MemberForm
    fieldsets = [
        # missing avatar_url
        ('Personal Information',      {'fields': [ 'first_name', 'last_name', 'gender', 'birthday', 'emergency_number', 'email', 'joined_date', 'grade' ]}),
        ('Still attending?',          {'fields': ['activation']})
    ]
    inlines = [AddressInline, MemberPhoneInline, BeltInline, ParentInline, USJF_MembershipInline, FeeInline, TournamentInline]

    list_display = ('first_name', 'last_name', 'emergency_number', 'gen_qrcode')
    list_filter = ['activation', 'gender']
    ordering = ['first_name']
    save_on_top = True

class AnnounceAdmin(admin.ModelAdmin):
    list_display = ('subject', 'pub_date')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('event', 'days', 'repetitive')

admin.site.register(Member, MemberAdmin)
admin.site.register(Announce, AnnounceAdmin)
admin.site.register(Notification, NotificationAdmin)
