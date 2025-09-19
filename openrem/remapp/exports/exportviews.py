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
..  module:: exportviews.py
    :synopsis: Module to render appropriate content according to request, specific to the exports.

..  moduleauthor:: Ed McDonagh

"""

# Following two lines added so that sphinx autodocumentation works.
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'openremproject.settings'

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.urls import reverse

@csrf_exempt
@login_required
def ctcsv1(request):
    """View to launch celery task to export CT studies to csv file

    :param request: Contains the database filtering parameters. Also used to get user group.
    :type request: GET
    """
    from django.shortcuts import redirect
    from remapp.exports.exportcsv import exportCT2excel

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        job = exportCT2excel.delay(request.GET)

    return redirect('/openrem/export/')


@csrf_exempt
@login_required
def ctxlsx1(request):
    """View to launch celery task to export CT studies to xlsx file

    :param request: Contains the database filtering parameters. Also used to get user group.
    :type request: GET
    """
    from django.shortcuts import redirect
    from remapp.exports.xlsx import ctxlsx

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        job = ctxlsx.delay(request.GET)
    
    return redirect('/openrem/export/')

@csrf_exempt
@login_required
def flcsv1(request):
    """View to launch celery task to export fluoroscopy studies to csv file

    :param request: Contains the database filtering parameters. Also used to get user group.
    :type request: GET
    """
    from django.shortcuts import redirect
    from remapp.exports.exportcsv import exportFL2excel

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        job = exportFL2excel.delay(request.GET)
    
    return redirect('/openrem/export/')

@csrf_exempt
@login_required
def mgcsv1(request):
    """View to launch celery task to export mammography studies to csv file

    :param request: Contains the database filtering parameters. Also used to get user group.
    :type request: GET
    """
    from django.shortcuts import redirect
    from remapp.exports.exportcsv import exportMG2excel

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        job = exportMG2excel.delay(request.GET)
    
    return redirect('/openrem/export/')

@csrf_exempt
@login_required
def mgnhsbsp(request):
    """View to launch celery task to export mammography studies to csv file using a NHSBSP template

    :param request: Contains the database filtering parameters. Also used to get user group.
    :type request: GET
    """
    from django.shortcuts import redirect
    from remapp.exports.mg_csv_nhsbsp import mg_csv_nhsbsp

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        job = mg_csv_nhsbsp.delay(request.GET)
    
    return redirect('/openrem/export/')

@csrf_exempt
@login_required
def export(request):
    """View to list current and completed exports to track progress, download and delete

    :param request: Used to get user group.
    """
    import pkg_resources # part of setuptools
    from django.shortcuts import render
    from remapp.models import Exports
    from remapp.exports.exportcsv import exportCT2excel

    exptsks = Exports.objects.all().order_by('-export_date')
    
    current = exptsks.filter(status__contains = 'CURRENT')
    complete = exptsks.filter(status__contains = 'COMPLETE')
    errors = exptsks.filter(status__contains = 'ERROR')
    
    try:
        vers = pkg_resources.require("openrem")[0].version
    except:
        vers = ''
    admin = {'openremversion' : vers}

    if request.user.groups.filter(name="exportgroup"):
        admin['exportperm'] = True
    if request.user.groups.filter(name="admingroup"):
        admin['adminperm'] = True


    task_id = request.session.get('task_id')
    context = {
        'exptsks': exptsks,
        'current': current,
        'complete': complete,
        'errors': errors,
        'admin': admin,
        'task_id': task_id,
    }
    return render(request, 'remapp/exports.html', context)


@login_required
def download(request, file_name):
    """View to handle downloads of files from the server

    Originally used for download of the export spreadsheets, now also used
    for downloading the patient size import logfiles.

    :param request: Used to get user group.
    :param file_name: Passes name of file to be downloaded.
    :type filename: string

    """
    import mimetypes
    import os
    from django.utils.encoding import smart_str
    from django.shortcuts import redirect
    from django.conf import settings

    if request.user.groups.filter(name="exportgroup") or request.user.groups.filter(name="admingroup"):
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        if not os.path.exists(file_path):
            return redirect('/openrem/export/')
        file_mimetype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        response = FileResponse(open(file_path, 'rb'), content_type=file_mimetype, as_attachment=True)
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
        return response
    else:
        return redirect('/openrem/export/')
        
@csrf_exempt
@login_required
def deletefile(request):
    """View to delete export files from the server

    :param request: Contains the task ID
    :type request: POST
    """
    import os, sys
    from django.http import HttpResponseRedirect
    from django.contrib import messages
    from django.conf import settings
    from remapp.models import Exports
    from remapp.exports import exportviews
    
    
    for task in request.POST:
        exports = Exports.objects.filter(task_id__exact = request.POST[task])
        for export in exports:
            try:
                export.filename.delete()
                export.delete()
                messages.success(request, "Export file and database entry deleted successfully.")
            except OSError as e:
                messages.error(request, "Export file delete failed - please contact an administrator. Error({0}): {1}".format(e.errno, e.strerror))
            except:
                messages.error(request, "Unexpected error - please contact an administrator: {0}".format(sys.exc_info()[0]))
    
    return HttpResponseRedirect(reverse('export'))

@login_required
def export_abort(request, pk):
    """View to abort current export job

    :param request: Contains the task primary key
    :type request: POST
    """
    from celery.task.control import revoke
    from django.http import HttpResponseRedirect
    from django.shortcuts import render, redirect, get_object_or_404
    from remapp.models import Exports

    export = get_object_or_404(Exports, pk=pk)    

    if request.user.groups.filter(name="admingroup") or request.user.groups.filter(name="exportgroup"):
        revoke(export.task_id, terminate=True)
        export.delete()

    return HttpResponseRedirect("/openrem/export/")
