from django.conf import settings

GOOGLE_API_KEY = settings.GOOGLE_API_KEY
MAPBOX_API_KEY = settings.MAPBOX_API_KEY

def global_settings(request):
    return{
        'GOOGLE_API_KEY': GOOGLE_API_KEY,
        'MAPBOX_API_KEY': MAPBOX_API_KEY,
    }