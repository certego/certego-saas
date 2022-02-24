from certego_saas.settings import certego_apps_settings


def host(request):
    """
    Custom context processor that injects the
    ``HOST_URI`` and ``HOST_NAME`` setting variables into every template.
    """
    return {
        "host_uri": certego_apps_settings.HOST_URI,
        "host_name": certego_apps_settings.HOST_NAME,
    }
