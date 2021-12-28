from certego_saas.settings import certego_apps_settings


def host(request):
    return {
        "host_uri": certego_apps_settings.HOST_URI,
        "host_name": certego_apps_settings.HOST_NAME,
    }
