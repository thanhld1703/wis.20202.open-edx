BUG: URL for downloading csv report is not correct

After logging in as the course creator, on instructor section in course-about page, you can download the report files by 
accessing the link at the end of the page. However, running on the current code will give you an error because of few 
shortages of configuration.

// insert illustration of bug

### Solution
1. Modify devstack.yml
- Open `edx-platform/lms/devsatck.yml` and looking for the section of `GRADES_DOWNLOAD`. In my case, it is
```yaml
GRADES_DOWNLOAD:
    BUCKET: ''
    ROOT_PATH: /tmp/edx-s3/grades
    STORAGE_CLASS: django.core.files.storage.FileSystemStorage
    STORAGE_KWARGS:
        location: /tmp/edx-s3/grades 
    STORAGE_TYPE: ''
```
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