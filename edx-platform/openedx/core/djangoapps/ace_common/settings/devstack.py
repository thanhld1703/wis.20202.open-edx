"""
Settings for edX ACE on devstack.
"""


from openedx.core.djangoapps.ace_common.settings import common


def plugin_settings(settings):
    """
    Override common settings and use `file_email` for better debugging.
    """
    common.plugin_settings(settings)

    settings.ACE_ENABLED_CHANNELS = [
        'django_email'
    ]

    settings.ACE_CHANNEL_DEFAULT_EMAIL = 'django_email'
    settings.ACE_CHANNEL_TRANSACTIONAL_EMAIL = 'django_email'
