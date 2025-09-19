#    OpenREM - Radiation Exposure Monitoring tools for the physicist
#    Copyright (C) 2012,2013  The Royal Marsden NHS Foundation Trust
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    Additional permission under section 7 of GPLv3:
#    You shall not make any use of the name of The Royal Marsden NHS
#    Foundation trust in connection with this Program in any press or 
#    other public announcement without the prior written consent of 
#    The Royal Marsden NHS Foundation Trust.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
..  module:: urls.
    :synopsis: Module to match URLs and pass over to views or export modules.

..  moduleauthor:: Ed McDonagh

"""

from django.urls import re_path
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from remapp.models import Accumulated_projection_xray_dose, General_study_module_attributes
from remapp import views
from remapp.exports import exportviews
# from remapp.exports import xlsx


urlpatterns = [
    re_path(r'^$', views.openrem_home, name='home'),
    
    re_path(r'^rf/$', views.rf_summary_list_filter, name='rf_summary_list'),
    re_path(r'^rf/(?P<pk>\d+)/$',
        login_required(DetailView.as_view(
            model=General_study_module_attributes,
            template_name='remapp/rfdetail.html'))),

    re_path(r'^ct/$', views.ct_summary_list_filter, name='ct_summary_list'),
    re_path(r'^ct/(?P<pk>\d+)/$',
        login_required(DetailView.as_view(
            model=General_study_module_attributes,
            template_name='remapp/ctdetail.html'))),

    re_path(r'^ct$', views.ct_summary_list_filter),

    re_path(r'^mg/$', views.mg_summary_list_filter, name='mg_summary_list'),
    re_path(r'^mg/(?P<pk>\d+)/$',
        login_required(DetailView.as_view(
            model=General_study_module_attributes,
            template_name='remapp/mgdetail.html'))),

    re_path(r'^delete/(?P<pk>\d+)$', views.study_delete, name='study_delete'),
    re_path(r'^admin/sizeupload$', views.size_upload, name='size_upload'),
    re_path(r'^admin/sizeprocess/(?P<pk>\d+)/$', views.size_process, name='size_process'),
    re_path(r'^admin/sizeimports$', views.size_imports, name='size_imports'),
    re_path(r'^admin/sizedelete$', views.size_delete, name='size_delete'),
    re_path(r'^admin/sizeimport/abort/(?P<pk>\d+)$', views.size_abort, name='size_abort'),
]

urlpatterns += [
    re_path(r'^export/$', exportviews.export, name='export'),
    re_path(r'^exportctcsv1/$', exportviews.ctcsv1, name='export_ctcsv1'),
    re_path(r'^exportctxlsx1/$', exportviews.ctxlsx1, name='export_ctxlsx1'),
    re_path(r'^exportflcsv1/$', exportviews.flcsv1, name='export_flcsv1'),
    re_path(r'^exportmgcsv1/$', exportviews.mgcsv1, name='export_mgcsv1'),
    re_path(r'^exportmgnhsbsp/$', exportviews.mgnhsbsp, name='export_mgnhsbsp'),
    re_path(r'^download/(?P<file_name>.+)$', exportviews.download, name='download'),
    re_path(r'^deletefile/$', exportviews.deletefile, name='deletefile'),
    re_path(r'^export/abort/(?P<pk>\d+)$', exportviews.export_abort, name='export_abort'),
]

# urlpatterns += [
#     re_path(r'^xlsx/openrem/ct/', xlsx.ctxlsx, name='xlsx_ctxlsx'),
# ]

