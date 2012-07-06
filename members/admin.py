from datetime import datetime, timedelta, date

from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField
from django.contrib import admin
from django.http import HttpResponse

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
from members.models import Attendance
from members.models import Account
from members.models import Login_record

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from google.appengine.ext import webapp
from google.appengine.api import urlfetch


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

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1

class MemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['emergency_number'] = USPhoneNumberField()

def add_to_zipfile(zfile, url, fname):
    contents = urlfetch.fetch(url).content
    zfile.writestr(fname, contents)

def gen_qrcodes_zipfile(modeladmin, request, queryset):
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qrcode_ouput.zip"'

    with closing(ZipFile(response, "w", ZIP_DEFLATED)) as outfile:
        for m in queryset:
            data = 'http://norwalkjudo.appspot.com/members/%i/' % (m.pk, )
            url = 'https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=%s&chld=L|0' % (data,)
            add_to_zipfile(outfile, url, '%s %s.png' % (m.first_name, m.last_name))
    return response
gen_qrcodes_zipfile.short_description = 'Generate the qrcode(s)'


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
        data = 'http://norwalkjudo.appspot.com/members/%i/' % (obj.pk, )
        size = 200
        error_corrction = 'L'
        url = 'https://chart.googleapis.com/chart?cht=qr&chs=%ix%i&chl=%s&chld=%s|0' % (size, size, data, error_corrction)
        return '<a href=%s target=_blank>View</a>' % (url,)
    gen_qrcode.allow_tags = True
    gen_qrcode.short_description = 'QR Code'

    def is_checked(self, obj):
        time = datetime.now() + timedelta(hours=-8)
        today = time.date()
        attendance_list = obj.attendance_set.all().order_by('date').reverse()
        try:
            if attendance_list[0].date == today:
                return True
        except IndexError:
            return False
        return False
    is_checked.short_description = 'Attend Today'
    is_checked.boolean = True

    form = MemberForm
    fieldsets = [
        # missing avatar_url
        ('Personal Information',      {'fields': [ 'first_name', 'last_name', 'gender', 'birthday', 'emergency_number', 'email', 'joined_date', 'grade' ]}),
        ('Still attending?',          {'fields': ['activation']})
    ]
    inlines = [AddressInline, MemberPhoneInline, BeltInline, ParentInline, USJF_MembershipInline, FeeInline, TournamentInline, AttendanceInline]

    list_display = ('first_name', 'last_name', 'emergency_number', 'gen_qrcode', 'is_checked')
    list_filter = ['activation', 'gender']
    actions = [gen_qrcodes_zipfile, 'check_in_members']
    ordering = ['first_name']
    save_on_top = True

    def check_in_members(self, request, queryset):
        for m in queryset:
            time = datetime.now() + timedelta(hours=-8)
            today = time.date()
            attendance_list = m.attendance_set.all().order_by('date').reverse()
            try:
                if attendance_list[0].date == today:
                    continue
            except IndexError:
                pass
            m.attendance_set.create(date=today)
            m.save()
        if len(queryset) == 0:
            msg = '1 member was'
        else:
            msg = '%s members were' % len(queryset)
        self.message_user(request, '%s successfully checked in today!' % msg)
    check_in_members.short_description = 'Check in member(s) today'

class AnnounceAdmin(admin.ModelAdmin):
    list_display = ('subject', 'pub_date')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('event', 'days', 'repetitive')

class LoginRecordInline(admin.TabularInline):
    model = Login_record
    extra = 0
    
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'permission_level')
    inlines = [LoginRecordInline]

admin.site.register(Member, MemberAdmin)
admin.site.register(Announce, AnnounceAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Account, AccountAdmin)
