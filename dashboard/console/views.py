from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Log
from .forms import UserForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
import googlemaps
from .context_processors import GOOGLE_API_KEY


def get_logs(request, status):
    # status filter:
    ## i : all logs
    ## a : new logs
    ## w : processing logs
    ## r : resolved logs

    if request.is_ajax():
        try:
            if status == 'i':
                logs = Log.objects.all()
            else:
                logs = Log.objects.filter(status=status)
        except Log.DoesNotExist:
            raise Http404("Log does not exist")
        logs_json = serializers.serialize('json', logs)
        return HttpResponse(logs_json, content_type='application/json')
    else:
        raise Http404("Log does not exist")


def sync_db(request):
    if request.method == 'POST':
        status = request.POST['status']
        response = requests.get('http://8199bb70.ngrok.io/rlogs/?status=a')     # get only the active records (only they will have new entries)
        if response.status_code == 200:
            incoming_logs = response.json()
            for log in incoming_logs:
                _server_db_id = log['id']
                _timestamp = log['timestamp']
                _core_id = log['core_id']
                try:
                    Log.objects.get(server_db_id=_server_db_id)
                except ObjectDoesNotExist:
                    l = Log(server_db_id=_server_db_id, timestamp=_timestamp, emergency_type=log['emergency_type'],
                            core_id=_core_id, latitude=log['latitude'], longitude=log['longitude'],
                            accuracy=log['accuracy'], status=log['status'])
                    l.save_log()
            return HttpResponse("status = " + str(status))
        else:
            return HttpResponse("No logs found!")


@login_required
def show_logs(request, status):
    if status == "all":
        return render(request, 'console/logs-all.html')
    elif status == "new":
        return render(request, 'console/logs-new.html')
    elif status == "processing":
        return render(request, 'console/logs-processing.html')
    elif status == "resolved":
        return render(request, 'console/logs-resolved.html')
    else:
        return render(request, 'console/404.html')


@login_required
def request_detail(request, pk):
    try:
        log = Log.objects.get(pk = pk)
        address = request.user.profile.location.strip()
        tokens = address.split(' ')
        source = '+'.join(tokens)
        return render(request, 'console/detail.html', {
            'log': log,
            'source': source,
        })
    except ObjectDoesNotExist:
        return render(request, 'console/404.html')

@login_required
def update_status(request, pk, status):
    log = get_object_or_404(Log, pk=pk)

    if status == "d":
        log.delete()
        return HttpResponseRedirect(reverse('console:show_logs', args=['all']))

    log.status = status
    log.save_log()

    patch_url = "http://8199bb70.ngrok.io/rlogs/?status=" + str(status) + "&id=" + str(log.server_db_id)
    response = requests.get(patch_url)

    if status == "w":
        return HttpResponseRedirect(reverse('console:show_logs', args=['processing']))
    elif status == "r":
        return HttpResponseRedirect(reverse('console:show_logs', args=['resolved']))


@login_required
def analytics_view(request, feature):
    if feature == 'a':
        logs = Log.objects.all()
    elif feature == 'p':
        logs = Log.objects.filter(emergency_type = 'police')
    elif feature == 'm':
        logs = Log.objects.filter(emergency_type='medical')

    data = []
    for log in logs:
        location = (log.latitude, log.longitude)
        data.append(location)

    gamps = googlemaps.Client(key = GOOGLE_API_KEY)
    geocode_result = gamps.geocode(request.user.profile.location)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    data_js = json.dumps(data)
    return render(request, 'console/analytics.html', {
        'data': data_js,
        'c_lat': lat,
        'c_lng': lng
    })


@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return HttpResponseRedirect(reverse('console:profile'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'console/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })