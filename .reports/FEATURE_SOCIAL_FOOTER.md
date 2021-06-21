CUSTOMIZATION: SOCIAL NETWORK URL

The get_footer function which is shared in all footer GUI part provides a subsection, called social_links. This section 
display the social media associated with the current site, helping promote popularity and accessibility of the site. 
However, the current source code prevent the good as it always loads the default configuration, which contains nothing useful,
so we modify the api for footer to enable the dynamic.

// insert illustration of bug

### <u>Explanation</u>
- The configuration for the SOCIAL_MEDIA_FOOTER (You can find it in `edx-platform/lms/envs/common.py`)
```python
SOCIAL_MEDIA_FOOTER_NAMES = [
    "facebook",
    # etc
]

SOCIAL_MEDIA_FOOTER_DISPLAY = {
    "facebook": {
        # Translators: This is the website name of www.facebook.com.  Please
        # translate this the way that Facebook advertises in your language.
        "title": _("Facebook"),
        "icon": "fa-facebook-square",
        "action": _(u"Like {platform_name} on Facebook")
    },
    # etc
}
```
- The configuration is later loaded by `edx-platform/lms/djangoapps/branding/api.py`. This module will create data to 
  display in footer. The critical code is
```python
def _footer_social_links():
    platform_name = configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME)
    links = []

    for social_name in settings.SOCIAL_MEDIA_FOOTER_NAMES:
        display = settings.SOCIAL_MEDIA_FOOTER_DISPLAY.get(social_name, {})
        links.append(
            {
                "name": social_name,
                "title": six.text_type(display.get("title", "")),
                "url": settings.SOCIAL_MEDIA_FOOTER_URLS.get(social_name, "#"),
                "icon-class": display.get("icon", ""),
                "action": six.text_type(display.get("action", "")).format(platform_name=platform_name),
            }
        )
```
- Because the current code reads from only the concrete configuration, dynamic site updates show no works.

### <u>Solution</u>
- Change the code into the following snippet:
```python
def _footer_social_links():
    platform_name = configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
    social_names = configuration_helpers.get_value('SOCIAL_MEDIA_FOOTER_NAMES', settings.SOCIAL_MEDIA_FOOTER_NAMES)
    social_displays = configuration_helpers.get_value('SOCIAL_MEDIA_FOOTER_DISPLAY', settings.SOCIAL_MEDIA_FOOTER_NAMES)
    links = []

    for social_name in social_names:
        display = social_displays.get(social_name, {})
        links.append(
            {
                "name": social_name,
                "title": six.text_type(display.get("title", "")),
                "url": six.text_type(display.get("url", "#")),
                "icon-class": display.get("icon", ""),
                "action": six.text_type(display.get("action", "")).format(platform_name=platform_name),
            }
        )
    return links
```
### <u>Test</u>
1. Go to admin Site configuration page on <edx-host>:18000/admin
2. Change the site configuration by modify the json content. In this case, we want to configure the social media footer,
 thus we add these following data:
```json
{
  "COURSE_CATALOG_API_URL": "http://edx.devstack.discovery:18381/api/v1/",
  "PLATFORM_NAME": "Agile Academy",
  "SOCIAL_MEDIA_FOOTER_NAMES": [
    "facebook"
  ],
  "SOCIAL_MEDIA_FOOTER_DISPLAY": {
    "facebook": {
      "title": "Facebook",
      "icon-class": "fa-facebook-square",
      "url": "https://www.facebook.com/hocvienagile",
      "action": "Like {platform_name} on Facebook"
    }
  }
}
```
3. Press SAVE and reload the LMS page