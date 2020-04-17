from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Log
from .forms import UserForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import requests

def index(request):
    response = requests.get('http://8199bb70.ngrok.io/rlogs/')
    if response.status_code == 200:
        incoming_logs = response.json()
        for log in incoming_logs:
            _server_db_id = log['id']
            _timestamp = log['timestamp']
            _core_id = log['core_id']
            try:
                # Log.objects.get(timestamp = _timestamp, core_id = _core_id)
                Log.objects.get(server_db_id = _server_db_id)
            except ObjectDoesNotExist:
                l = Log(server_db_id = _server_db_id, timestamp = _timestamp, emergency_type = log['emergency_type'], core_id = _core_id, latitude = log['latitude'], longitude = log['longitude'], accuracy = log['accuracy'], status = log['status'])
                l.save_log()

    try:
        new_logs = Log.objects.filter(status="a")
        processing_logs = Log.objects.filter(status="w")
        resolved_logs = Log.objects.filter(status="r")
    except Log.DoesNotExist:
        raise Http404("Log does not exist")

    context = {
        'n_logs': new_logs,
        'p_logs': processing_logs,
        'r_logs': resolved_logs
    }
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
    try:
        log = Log.objects.get(pk = pk)
        address = request.user.profile.location.strip()
        tokens = address.split(' ')
        source = '+'.join(tokens)
        return render(request, 'console/detail.html', {
            'log': log,
            'source': source,
            'api_key': 'AIzaSyARRcMNgSrGPV5mOURKpwvjIJ3uygQs8vs'
        })
    except ObjectDoesNotExist:
        return render(request, 'console/404.html', {})


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