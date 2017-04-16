from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('reports.views',
    url(r'^reception_day/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'reception_day', name='reception_day'),
    url(r'^reception_visits/$', 'reception_visits', name='reception_visits'),
    url(r'^menu/$', 'menu', name='reports_menu'),
    url(r'^sells/(?P<year>\d{4})/(?P<month>\d{2})/(?P<other>\d{1})/$', 'sells', name='r_sells'),
    url(r'^visits/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'visits', name='r_visits'),
    url(r'^e_visits/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'e_visits', name='r_e_visits'),
    url(r'^ptt/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'ptt', name='r_ptt'),
    url(r'^manager/(?P<year>\d{4})/(?P<month>\d{2})/$', 'manager', name='r_manager'),
    url(r'^debtors/(?P<manager>\d+)/$', 'debtors', name='r_debtors'),
    url(r'^debtors/menu/$', 'debtors_menu', name='r_debtors_menu'),
    url(r'^employees/$', 'employees', name='r_employees'),
    url(r'^trainer_ptt/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'trainer_ptt', name='r_trainer_ptt'),
    url(r'^reception/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<other>\d{1})/$', 'reception', name='r_reception'),
    url(r'^contract_end/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'contract_end', name='r_contract_end'),
    url(r'^manager_sells/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'manager_sells', name='r_manager_sells'),
    url(r'^organizer/(?P<syear>\d{4})/(?P<smonth>\d{2})/(?P<sday>\d{2})/(?P<eyear>\d{4})/(?P<emonth>\d{2})/(?P<eday>\d{2})/$', 'organizer', name='r_organizer'),
    url(r'^organizerf/$', 'organizer_full', name='r_organizer_f'),

    url(r'^departments_names/$', 'departments_names', name='r_departments_names'),
)