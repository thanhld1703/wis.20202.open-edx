BUG: URL for downloading csv report is not correct

After logging in as the course creator, on instructor section in course-about page, you can download the report files by 
accessing the link at the end of the page. However, running on the current code will give you an error because of few 
shortages of configuration.

// insert illustration of bug

### <u>Explanation</u>
- The configuration for the report storage is GRADES_DOWNLOAD (You can find it in `edx-platform/lms/devsatck.yml`)
```yaml
GRADES_DOWNLOAD:
    BUCKET: ''
    ROOT_PATH: /tmp/edx-s3/grades
    STORAGE_CLASS: django.core.files.storage.FileSystemStorage
    STORAGE_KWARGS:
        location: /tmp/edx-s3/grades 
    STORAGE_TYPE: ''
```
- The configuration is later loaded by `/edx-platform/lms/djangoapps/instructor_task/models.py`. This module will create
   url to download. The critical code is
```python
    def from_config(cls, config_name):
        """
        By default, the default file storage specified by the `DEFAULT_FILE_STORAGE`
        setting will be used. To configure the storage used, add a dict in
        settings with the following fields::

            STORAGE_CLASS : The import path of the storage class to use. If
                            not set, the DEFAULT_FILE_STORAGE setting will be used.
            STORAGE_KWARGS : An optional dict of kwargs to pass to the storage
                             constructor. This can be used to specify a
                             different S3 bucket or root path, for example.

        Reference the setting name when calling `.from_config`.
        """
        return cls(
            getattr(settings, config_name).get('STORAGE_CLASS'),
            getattr(settings, config_name).get('STORAGE_KWARGS'),
        )
```
- Because the current configuration lacked few essential parameters, Django used the default parameter, which results in
  wrong builds of URLs.

### <u>Solution</u>
1. Modify devstack.yml of LMS module
- Open `edx-platform/lms/devsatck.yml` and looking for the section of `GRADES_DOWNLOAD`. In my case, it is

- Fill the section `STORAGE_KWARGS`
```yaml
    STORAGE_KWARGS:
        location: /tmp/edx-s3/grades
        base_url: /reports/grades
```
2. Modify urls.py of LMS module
- Open `edx-platform/lms/urls.py` and looking for the section of static URL (about line 900 and under `if settings.DEBUG `).
In my case, it is
```python.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
- Add these following code under the section
```
    urlpatterns += static(
        settings.GRADES_DOWNLOAD['STORAGE_KWARGS']['base_url'],
        document_root=settings.GRADES_DOWNLOAD['STORAGE_KWARGS']['location']
    )
```
3. Restart the lms service
- Move to root folder of the project and navigate into `devstack` directory
- Run
```shell
make lms-restart
```