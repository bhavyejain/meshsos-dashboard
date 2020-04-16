from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Log
from django.http import Http404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import requests
import googlemaps

def index(request):
    response = requests.get('http://8199bb70.ngrok.io/rlogs/')
    if response.status_code == 200:
        incoming_logs = response.json()
        for log in incoming_logs:
            _timestamp = log['timestamp']
            _core_id = log['core_id']
            try:
                Log.objects.get(timestamp = _timestamp, core_id = _core_id)
            except ObjectDoesNotExist:
                l = Log(timestamp = _timestamp, emergency_type = log['emergency_type'], core_id = _core_id, latitude = log['latitude'], longitude = log['longitude'], accuracy = log['accuracy'], status = log['status'])
                l.save_log()

    try:
        logs = Log.objects.all()
    except Log.DoesNotExist:
        raise Http404("Log does not exist")

    context = {'logs': logs}
    return render(request, 'console/logs.html', context)


def new_requests(request):
    try:
        logs = Log.objects.filter(status='a')
    except Log.DoesNotExist:
        raise Http404("Active logs don't exist")
    context = {'logs': logs}
    return render(request, 'console/logs-new.html', context)


def processing_requests(request):
    try:
        logs = Log.objects.filter(status='w')
    except Log.DoesNotExist:
        raise Http404("Active logs don't exist")
    context = {'logs': logs}
    return render(request, 'console/logs-processing.html', context)


def resolved_requests(request):
    try:
        logs = Log.objects.filter(status='r')
    except Log.DoesNotExist:
        raise Http404("Active logs don't exist")
    context = {'logs': logs}
    return render(request, 'console/logs-resolved.html', context)


def request_detail(request, pk):
    log = get_object_or_404(Log, pk = pk)
    return render(request, 'console/detail.html', {
        'log': log,
        'source': '10, Ballupur Road, Dehradun, Uttarakhand, India',
        'api_key': 'AIzaSyARRcMNgSrGPV5mOURKpwvjIJ3uygQs8vs'
    })


def update_status(request, pk, status):
    log = get_object_or_404(Log, pk=pk)

    if status == "d":
        log.delete()
        return HttpResponseRedirect(reverse('console:index'))

    log.status = status
    log.save_log()
    if status == "w":
        return HttpResponseRedirect(reverse('console:processing-logs'))
    elif status == "r":
        return HttpResponseRedirect(reverse('console:resolved-logs'))


'''
get location from address:

gmaps = googlemaps.Client(key='')
geocode_result = gmaps.geocode(<address>)
origin_lat = geocode_result[0]['geometry']['location']['lat']
origin_lon = lat = geocode_result[0]['geometry']['location']['lng']
'''