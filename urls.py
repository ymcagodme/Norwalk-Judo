from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'members.views.index'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout$', 'members.views.user_logout'),
    url(r'^query_all$', 'members.views.query_all'),
    url(r'^gen_email_info$', 'members.views.gen_email_info'),
    url(r'^gen_csv$', 'members.views.gen_csv'),
    url(r'^gen_csv$', 'members.views.gen_csv'),
    url(r'^gen_tournament_report$', 'members.views.gen_tournament_report'),
    url(r'^serve_csv$', 'members.views.serve_csv'),
    url(r'^announce$', 'members.views.announce'),
    url(r'^notify/expiration$', 'members.views.notify_expiration'),
    url(r'^member/(?P<pk>\d+)/$', 'members.views.member_query'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
)
