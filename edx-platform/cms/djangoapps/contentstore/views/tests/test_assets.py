"""
Unit tests for the asset upload endpoint.
"""


import json
from datetime import datetime
from io import BytesIO

import mock
import six
from ddt import data, ddt
from django.conf import settings
from django.test.utils import override_settings
from mock import patch
from opaque_keys.edx.keys import AssetKey
from opaque_keys.edx.locator import CourseLocator
from PIL import Image
from pytz import UTC

from cms.djangoapps.contentstore.tests.utils import CourseTestCase
from cms.djangoapps.contentstore.utils import reverse_course_url
from cms.djangoapps.contentstore.views import assets
from common.djangoapps.static_replace import replace_static_urls
from xmodule.assetstore import AssetMetadata
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_importer import import_course_from_xml

TEST_DATA_DIR = settings.COMMON_TEST_DATA_ROOT

MAX_FILE_SIZE = settings.MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB * 1000 ** 2

FEATURES_WITH_CERTS_ENABLED = settings.FEATURES.copy()
FEATURES_WITH_CERTS_ENABLED['CERTIFICATES_HTML_VIEW'] = True


@override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
class AssetsTestCase(CourseTestCase):
    """
    Parent class for all asset tests.
    """
    def setUp(self):
        super(AssetsTestCase, self).setUp()
        self.url = reverse_course_url('assets_handler', self.course.id)

    def upload_asset(self, name="asset-1", asset_type='text'):
        """
        Post to the asset upload url
        """
        asset = self.get_sample_asset(name, asset_type)
        response = self.client.post(self.url, {"name": name, "file": asset})
        return response

    def get_sample_asset(self, name, asset_type='text'):
        """
        Returns an in-memory file of the specified type with the given name for testing
        """
        sample_asset = BytesIO()
        sample_file_contents = b"This file is generated by python unit test"
        if asset_type == 'text':
            sample_asset.name = '{name}.txt'.format(name=name)
            sample_asset.write(sample_file_contents)
        elif asset_type == 'image':
            image = Image.new("RGB", size=(50, 50), color=(256, 0, 0))
            image.save(sample_asset, 'jpeg')
            sample_asset.name = '{name}.jpg'.format(name=name)
        elif asset_type == 'opendoc':
            sample_asset.name = '{name}.odt'.format(name=name)
            sample_asset.write(sample_file_contents)
        sample_asset.seek(0)
        return sample_asset


class BasicAssetsTestCase(AssetsTestCase):
    """
    Test getting assets via html w/o additional args
    """
    def test_basic(self):
        resp = self.client.get(self.url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)

    def test_static_url_generation(self):

        course_key = CourseLocator('org', 'class', 'run')
        location = course_key.make_asset_key('asset', 'my_file_name.jpg')
        path = StaticContent.get_static_path_from_location(location)
        self.assertEqual(path, '/static/my_file_name.jpg')

    def test_pdf_asset(self):
        module_store = modulestore()
        course_items = import_course_from_xml(
            module_store,
            self.user.id,
            TEST_DATA_DIR,
            ['toy'],
            static_content_store=contentstore(),
            verbose=True
        )
        course = course_items[0]
        url = reverse_course_url('assets_handler', course.id)

        # Test valid contentType for pdf asset (textbook.pdf)
        resp = self.client.get(url, HTTP_ACCEPT='application/json')
        self.assertContains(resp, "/c4x/edX/toy/asset/textbook.pdf")
        asset_location = AssetKey.from_string('/c4x/edX/toy/asset/textbook.pdf')
        content = contentstore().find(asset_location)
        # Check after import textbook.pdf has valid contentType ('application/pdf')

        # Note: Actual contentType for textbook.pdf in asset.json is 'text/pdf'
        self.assertEqual(content.content_type, 'application/pdf')

    def test_relative_url_for_split_course(self):
        """
        Test relative path for split courses assets
        """
        with modulestore().default_store(ModuleStoreEnum.Type.split):
            module_store = modulestore()
            course_id = module_store.make_course_key('edX', 'toy', '2012_Fall')
            import_course_from_xml(
                module_store,
                self.user.id,
                TEST_DATA_DIR,
                ['toy'],
                static_content_store=contentstore(),
                target_id=course_id,
                create_if_not_present=True
            )
            course = module_store.get_course(course_id)

            filename = 'sample_static.html'
            html_src_attribute = '"/static/{}"'.format(filename)
            asset_url = replace_static_urls(html_src_attribute, course_id=course.id)
            url = asset_url.replace('"', '')
            base_url = url.replace(filename, '')

            self.assertIn("/{}".format(filename), url)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

            # simulation of html page where base_url is up-to asset's main directory
            # and relative_path is dom element with its src
            relative_path = 'just_a_test.jpg'
            # browser append relative_path with base_url
            absolute_path = base_url + relative_path

            self.assertIn("/{}".format(relative_path), absolute_path)
            resp = self.client.get(absolute_path)
            self.assertEqual(resp.status_code, 200)


class PaginationTestCase(AssetsTestCase):
    """
    Tests the pagination of assets returned from the REST API.
    """
    def test_json_responses(self):
        """
        Test the ajax asset interfaces
        """
        self.upload_asset("asset-1")
        self.upload_asset("asset-2")
        self.upload_asset("asset-3")
        self.upload_asset("asset-4", "opendoc")

        # Verify valid page requests
        self.assert_correct_asset_response(self.url, 0, 4, 4)
        self.assert_correct_asset_response(self.url + "?page_size=2", 0, 2, 4)
        self.assert_correct_asset_response(
            self.url + "?page_size=2&page=1", 2, 2, 4)
        self.assert_correct_sort_response(self.url, 'date_added', 'asc')
        self.assert_correct_sort_response(self.url, 'date_added', 'desc')
        self.assert_correct_sort_response(self.url, 'display_name', 'asc')
        self.assert_correct_sort_response(self.url, 'display_name', 'desc')
        self.assert_correct_filter_response(self.url, 'asset_type', '')
        self.assert_correct_filter_response(self.url, 'asset_type', 'OTHER')
        self.assert_correct_filter_response(
            self.url, 'asset_type', 'Documents')
        self.assert_correct_filter_response(
            self.url, 'asset_type', 'Documents,Images')
        self.assert_correct_filter_response(
            self.url, 'asset_type', 'Documents,OTHER')

        self.assert_correct_text_search_response(self.url, 'asset-1.txt', 1)
        self.assert_correct_text_search_response(self.url, 'asset-1', 1)
        self.assert_correct_text_search_response(self.url, 'AsSeT-1', 1)
        self.assert_correct_text_search_response(self.url, '.txt', 3)
        self.assert_correct_text_search_response(self.url, '2', 1)
        self.assert_correct_text_search_response(self.url, 'asset 2', 1)
        self.assert_correct_text_search_response(self.url, '2 asset', 1)
        self.assert_correct_text_search_response(self.url, '*.txt', 0)
        self.assert_correct_asset_response(self.url + "?text_search=", 0, 4, 4)

        #Verify invalid request parameters
        self.assert_invalid_parameters_error(self.url, 'asset_type', 'edX')
        self.assert_invalid_parameters_error(self.url, 'asset_type', 'edX, OTHER')
        self.assert_invalid_parameters_error(self.url, 'asset_type', 'edX, Images')

        # Verify querying outside the range of valid pages
        self.assert_correct_asset_response(
            self.url + "?page_size=2&page=-1", 0, 2, 4)
        self.assert_correct_asset_response(
            self.url + "?page_size=2&page=2", 2, 2, 4)
        self.assert_correct_asset_response(
            self.url + "?page_size=3&page=1", 3, 1, 4)
        self.assert_correct_asset_response(
            self.url + "?page_size=1&page=5&asset_type=OTHER", 0, 1, 1)
        self.assert_correct_asset_response(
            self.url + "?page_size=1&page=5&asset_type=Images", 5, 0, 0)

    @mock.patch('xmodule.contentstore.mongo.MongoContentStore.get_all_content_for_course')
    def test_mocked_filtered_response(self, mock_get_all_content_for_course):
        """
        Test the ajax asset interfaces
        """
        asset_key = self.course.id.make_asset_key(
            AssetMetadata.GENERAL_ASSET_TYPE, 'test.jpg')
        upload_date = datetime(2015, 1, 12, 10, 30, tzinfo=UTC)
        thumbnail_location = [
            'c4x', 'edX', 'toy', 'thumbnail', 'test_thumb.jpg', None]

        mock_get_all_content_for_course.return_value = [
            [
                {
                    "asset_key": asset_key,
                    "displayname": "test.jpg",
                    "contentType": "image/jpg",
                    "url": "/c4x/A/CS102/asset/test.jpg",
                    "uploadDate": upload_date,
                    "id": "/c4x/A/CS102/asset/test.jpg",
                    "portable_url": "/static/test.jpg",
                    "thumbnail": None,
                    "thumbnail_location": thumbnail_location,
                    "locked": None
                }
            ],
            1
        ]
        # Verify valid page requests
        self.assert_correct_filter_response(self.url, 'asset_type', 'OTHER')

    def assert_correct_asset_response(self, url, expected_start, expected_length, expected_total):
        """
        Get from the url and ensure it contains the expected number of responses
        """
        resp = self.client.get(url, HTTP_ACCEPT='application/json')
        json_response = json.loads(resp.content.decode('utf-8'))
        assets_response = json_response['assets']
        self.assertEqual(json_response['start'], expected_start)
        self.assertEqual(len(assets_response), expected_length)
        self.assertEqual(json_response['totalCount'], expected_total)

    def assert_correct_sort_response(self, url, sort, direction):
        """
        Get from the url w/ a sort option and ensure items honor that sort
        """
        resp = self.client.get(
            url + '?sort=' + sort + '&direction=' + direction, HTTP_ACCEPT='application/json')
        json_response = json.loads(resp.content.decode('utf-8'))
        assets_response = json_response['assets']
        self.assertEqual(sort, json_response['sort'])
        self.assertEqual(direction, json_response['direction'])
        name1 = assets_response[0][sort]
        name2 = assets_response[1][sort]
        name3 = assets_response[2][sort]
        if direction == 'asc':
            self.assertLessEqual(name1, name2)
            self.assertLessEqual(name2, name3)
        else:
            self.assertGreaterEqual(name1, name2)
            self.assertGreaterEqual(name2, name3)

    def assert_correct_filter_response(self, url, filter_type, filter_value):
        """
        Get from the url w/ a filter option and ensure items honor that filter
        """

        filter_value_split = filter_value.split(',') if filter_value else []

        requested_file_extensions = []
        all_file_extensions = []

        for requested_filter in filter_value_split:
            if requested_filter == 'OTHER':
                for file_type in settings.FILES_AND_UPLOAD_TYPE_FILTERS:
                    all_file_extensions.extend(file_type)
            else:
                file_extensions = settings.FILES_AND_UPLOAD_TYPE_FILTERS.get(
                    requested_filter, None)
                if file_extensions is not None:
                    requested_file_extensions.extend(file_extensions)

        resp = self.client.get(
            url + '?' + filter_type + '=' + filter_value, HTTP_ACCEPT='application/json')
        json_response = json.loads(resp.content.decode('utf-8'))
        assets_response = json_response['assets']
        self.assertEqual(filter_value_split, json_response['assetTypes'])

        if filter_value != '':
            content_types = [asset['content_type'].lower()
                             for asset in assets_response]
            if 'OTHER' in filter_value_split:
                for content_type in content_types:
                    # content_type is either not any defined type (i.e. OTHER) or is a defined type (if multiple
                    # parameters including OTHER are used)
                    self.assertTrue(
                        content_type in requested_file_extensions or content_type not in all_file_extensions
                    )
            else:
                for content_type in content_types:
                    self.assertIn(content_type, requested_file_extensions)

    def assert_invalid_parameters_error(self, url, filter_type, filter_value):
        """
        Get from the url w/ invalid filter option(s) and ensure error is received
        """
        resp = self.client.get(
            url + '?' + filter_type + '=' + filter_value, HTTP_ACCEPT='application/json')
        self.assertEqual(resp.status_code, 400)

    def assert_correct_text_search_response(self, url, text_search, number_matches):
        """
        Get from the url w/ a text_search option and ensure items honor that search query
        """
        resp = self.client.get(
            url + '?text_search=' + text_search, HTTP_ACCEPT='application/json')
        json_response = json.loads(resp.content.decode('utf-8'))
        assets_response = json_response['assets']
        self.assertEqual(text_search, json_response['textSearch'])
        self.assertEqual(len(assets_response), number_matches)

        text_search_tokens = text_search.split()

        for asset_response in assets_response:
            for token in text_search_tokens:
                self.assertIn(token.lower(), asset_response['display_name'].lower())


@ddt
class UploadTestCase(AssetsTestCase):
    """
    Unit tests for uploading a file
    """
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.url = reverse_course_url('assets_handler', self.course.id)

    def test_happy_path(self):
        resp = self.upload_asset()
        self.assertEqual(resp.status_code, 200)

    def test_upload_image(self):
        resp = self.upload_asset("test_image", asset_type="image")
        self.assertEqual(resp.status_code, 200)

    @data(
        (int(MAX_FILE_SIZE / 2.0), "small.file.test", 200),
        (MAX_FILE_SIZE, "justequals.file.test", 200),
        (MAX_FILE_SIZE + 90, "large.file.test", 413),
    )
    @mock.patch('cms.djangoapps.contentstore.views.assets.get_file_size')
    def test_file_size(self, case, get_file_size):
        max_file_size, name, status_code = case

        get_file_size.return_value = max_file_size

        f = self.get_sample_asset(name=name)
        resp = self.client.post(self.url, {
            "name": name,
            "file": f
        })
        self.assertEqual(resp.status_code, status_code)


class DownloadTestCase(AssetsTestCase):
    """
    Unit tests for downloading a file.
    """
    def setUp(self):
        super(DownloadTestCase, self).setUp()
        self.url = reverse_course_url('assets_handler', self.course.id)
        # First, upload something.
        self.asset_name = 'download_test'
        resp = self.upload_asset(self.asset_name)
        self.assertEqual(resp.status_code, 200)
        self.uploaded_url = json.loads(resp.content.decode('utf-8'))['asset']['url']

    def test_download(self):
        # Now, download it.
        resp = self.client.get(self.uploaded_url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This file is generated by python unit test')

    def test_download_not_found_throw(self):
        url = self.uploaded_url.replace(self.asset_name, 'not_the_asset_name')
        resp = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 404)

    @patch('xmodule.modulestore.mixed.MixedModuleStore.find_asset_metadata')
    def test_pickling_calls(self, patched_find_asset_metadata):
        """ Tests if assets are not calling find_asset_metadata
        """
        patched_find_asset_metadata.return_value = None
        self.client.get(self.uploaded_url, HTTP_ACCEPT='text/html')
        self.assertFalse(patched_find_asset_metadata.called)


class AssetToJsonTestCase(AssetsTestCase):
    """
    Unit test for transforming asset information into something
    we can send out to the client via JSON.
    """
    @override_settings(LMS_BASE="lms_base_url")
    def test_basic(self):
        upload_date = datetime(2013, 6, 1, 10, 30, tzinfo=UTC)
        content_type = 'image/jpg'
        course_key = CourseLocator('org', 'class', 'run')
        location = course_key.make_asset_key('asset', 'my_file_name.jpg')
        thumbnail_location = course_key.make_asset_key('thumbnail', 'my_file_name_thumb.jpg')

        # pylint: disable=protected-access
        output = assets._get_asset_json("my_file", content_type, upload_date, location, thumbnail_location, True)

        self.assertEqual(output["display_name"], "my_file")
        self.assertEqual(output["date_added"], "Jun 01, 2013 at 10:30 UTC")
        self.assertEqual(output["url"], "/asset-v1:org+class+run+type@asset+block@my_file_name.jpg")
        self.assertEqual(
            output["external_url"], "lms_base_url/asset-v1:org+class+run+type@asset+block@my_file_name.jpg"
        )
        self.assertEqual(output["portable_url"], "/static/my_file_name.jpg")
        self.assertEqual(output["thumbnail"], "/asset-v1:org+class+run+type@thumbnail+block@my_file_name_thumb.jpg")
        self.assertEqual(output["id"], six.text_type(location))
        self.assertEqual(output['locked'], True)

        output = assets._get_asset_json("name", content_type, upload_date, location, None, False)
        self.assertIsNone(output["thumbnail"])


class LockAssetTestCase(AssetsTestCase):
    """
    Unit test for locking and unlocking an asset.
    """

    def test_locking(self):
        """
        Tests a simple locking and unlocking of an asset in the toy course.
        """
        def verify_asset_locked_state(locked):
            """ Helper method to verify lock state in the contentstore """
            asset_location = StaticContent.get_location_from_path('/c4x/edX/toy/asset/sample_static.html')
            content = contentstore().find(asset_location)
            self.assertEqual(content.locked, locked)

        def post_asset_update(lock, course):
            """ Helper method for posting asset update. """
            content_type = 'application/txt'
            upload_date = datetime(2013, 6, 1, 10, 30, tzinfo=UTC)
            asset_location = course.id.make_asset_key('asset', 'sample_static.html')
            url = reverse_course_url(
                'assets_handler', course.id, kwargs={'asset_key_string': six.text_type(asset_location)}
            )

            resp = self.client.post(
                url,
                # pylint: disable=protected-access
                json.dumps(assets._get_asset_json(
                    "sample_static.html", content_type, upload_date, asset_location, None, lock)),
                "application/json"
            )

            self.assertEqual(resp.status_code, 201)
            return json.loads(resp.content.decode('utf-8'))

        # Load the toy course.
        module_store = modulestore()
        course_items = import_course_from_xml(
            module_store,
            self.user.id,
            TEST_DATA_DIR,
            ['toy'],
            static_content_store=contentstore(),
            verbose=True
        )
        course = course_items[0]
        verify_asset_locked_state(False)

        # Lock the asset
        resp_asset = post_asset_update(True, course)
        self.assertTrue(resp_asset['locked'])
        verify_asset_locked_state(True)

        # Unlock the asset
        resp_asset = post_asset_update(False, course)
        self.assertFalse(resp_asset['locked'])
        verify_asset_locked_state(False)


class DeleteAssetTestCase(AssetsTestCase):
    """
    Unit test for removing an asset.
    """
    def setUp(self):
        """ Scaffolding """
        super(DeleteAssetTestCase, self).setUp()
        self.url = reverse_course_url('assets_handler', self.course.id)
        # First, upload something.
        self.asset_name = 'delete_test'
        self.asset = self.get_sample_asset(self.asset_name)

        response = self.client.post(self.url, {"name": self.asset_name, "file": self.asset})
        self.assertEqual(response.status_code, 200)
        self.uploaded_url = json.loads(response.content.decode('utf-8'))['asset']['url']

        self.asset_location = AssetKey.from_string(self.uploaded_url)
        self.content = contentstore().find(self.asset_location)

    def test_delete_asset(self):
        """ Tests the happy path :) """
        test_url = reverse_course_url(
            'assets_handler', self.course.id, kwargs={'asset_key_string': six.text_type(self.uploaded_url)})
        resp = self.client.delete(test_url, HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 204)

    def test_delete_image_type_asset(self):
        """ Tests deletion of image type asset """
        image_asset = self.get_sample_asset(self.asset_name, asset_type="image")
        thumbnail_image_asset = self.get_sample_asset('delete_test_thumbnail', asset_type="image")

        # upload image
        response = self.client.post(self.url, {"name": "delete_image_test", "file": image_asset})
        self.assertEqual(response.status_code, 200)
        uploaded_image_url = json.loads(response.content.decode('utf-8'))['asset']['url']

        # upload image thumbnail
        response = self.client.post(self.url, {"name": "delete_image_thumb_test", "file": thumbnail_image_asset})
        self.assertEqual(response.status_code, 200)
        thumbnail_url = json.loads(response.content.decode('utf-8'))['asset']['url']
        thumbnail_location = StaticContent.get_location_from_path(thumbnail_url)

        image_asset_location = AssetKey.from_string(uploaded_image_url)
        content = contentstore().find(image_asset_location)
        content.thumbnail_location = thumbnail_location
        contentstore().save(content)

        with mock.patch('opaque_keys.edx.locator.CourseLocator.make_asset_key') as mock_asset_key:
            mock_asset_key.return_value = thumbnail_location

            test_url = reverse_course_url(
                'assets_handler', self.course.id, kwargs={'asset_key_string': six.text_type(uploaded_image_url)})
            resp = self.client.delete(test_url, HTTP_ACCEPT="application/json")
            self.assertEqual(resp.status_code, 204)

    def test_delete_asset_with_invalid_asset(self):
        """ Tests the sad path :( """
        test_url = reverse_course_url(
            'assets_handler',
            self.course.id, kwargs={'asset_key_string': six.text_type("/c4x/edX/toy/asset/invalid.pdf")}
        )
        resp = self.client.delete(test_url, HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 404)

    def test_delete_asset_with_invalid_thumbnail(self):
        """ Tests the sad path :( """
        test_url = reverse_course_url(
            'assets_handler', self.course.id, kwargs={'asset_key_string': six.text_type(self.uploaded_url)})
        self.content.thumbnail_location = StaticContent.get_location_from_path('/c4x/edX/toy/asset/invalid')
        contentstore().save(self.content)
        resp = self.client.delete(test_url, HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 204)
