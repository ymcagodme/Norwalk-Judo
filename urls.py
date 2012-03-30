from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'members.views.index'),
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
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
