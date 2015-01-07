"""
Tests for mobile API utilities
"""

import ddt
from mock import patch
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from opaque_keys.edx.keys import CourseKey
from courseware.tests.factories import UserFactory
from student import auth
from student.models import CourseEnrollment

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from .utils import mobile_access_when_enrolled

ROLE_CASES = (
    (auth.CourseBetaTesterRole, True),
    (auth.CourseStaffRole, True),
    (auth.CourseInstructorRole, True),
    (None, False)
)


class MobileAPITestCase(ModuleStoreTestCase, APITestCase):
    """
    Base class for testing Mobile APIs.
    Subclasses are expected to define REVERSE_NAME to be used for django reverse URL.
    They may also override any of the methods defined in this class to control the behavior of the TestMixins.
    """
    def setUp(self):
        super(MobileAPITestCase, self).setUp()
        self.course = CourseFactory.create(mobile_available=True)
        self.user = UserFactory.create()
        self.password = 'test'
        self.username = self.user.username

    def tearDown(self):
        super(MobileAPITestCase, self).tearDown()
        self.logout()

    def login(self):
        """Login test user."""
        self.client.login(username=self.username, password=self.password)

    def logout(self):
        """Login test user."""
        self.client.logout()

    def enroll(self, course_id=None):
        """Enroll test user in test course."""
        CourseEnrollment.enroll(self.user, course_id or self.course.id)

    def unenroll(self, course_id=None):
        """Unenroll test user in test course."""
        CourseEnrollment.unenroll(self.user, course_id or self.course.id)

    def login_and_enroll(self, course_id=None):
        """Shortcut for both login and enrollment of the user."""
        self.login()
        self.enroll(course_id)

    def get_response(self, reverse_args=None, expected_response_code=200, **kwargs):
        """
        Helper method for calling endpoint, verifying and returning response.
        If expected_response_code is None, doesn't verify the response' status_code.
        """
        url = self.get_url(reverse_args, **kwargs)
        response = self.url_method(url, **kwargs)
        if expected_response_code is not None:
            self.assertEqual(response.status_code, expected_response_code)
        return response

    def get_url(self, reverse_args=None, **kwargs):  # pylint: disable=unused-argument
        """Base implementation that returns URL for endpoint that's being tested."""
        return reverse(self.REVERSE_NAME, kwargs=reverse_args)  # pylint: disable=no-member

    def url_method(self, url, **kwargs):  # pylint: disable=unused-argument
        """Base implementation that returns response from the GET method of the URL."""
        return self.client.get(url)


class MobileCourseAPITestCase(MobileAPITestCase):
    """
    Base class for testing Mobile APIs related to courses.
    """
    def get_url(self, reverse_args=None, **kwargs):  # pylint: disable=unused-argument
        reverse_args = reverse_args or {}
        reverse_args.update({'course_id': unicode(kwargs.get('course_id', self.course.id))})
        return super(MobileCourseAPITestCase, self).get_url(reverse_args, **kwargs)


class MobileUserAPITestCase(MobileAPITestCase):
    """
    Base class for testing Mobile APIs related to users.
    """
    def get_url(self, reverse_args=None, **kwargs):
        reverse_args = reverse_args or {}
        reverse_args.update({'username': kwargs.get('username', self.user.username)})
        return super(MobileUserAPITestCase, self).get_url(reverse_args, **kwargs)


class MobileUserCourseAPITestCase(MobileAPITestCase):
    """
    Base class for testing Mobile APIs related to both users and courses.
    """
    def get_url(self, reverse_args=None, **kwargs):
        reverse_args = reverse_args or {}
        reverse_args.update({
            'course_id': unicode(kwargs.get('course_id', self.course.id)),
            'username': kwargs.get('username', self.user.username)
        })
        return super(MobileUserCourseAPITestCase, self).get_url(reverse_args, **kwargs)


class MobileAuthTestMixin(object):
    """
    Test Mixin for testing APIs decorated with MobileView or mobile_view.
    """
    def test_no_auth(self):
        self.logout()
        self.get_response(expected_response_code=401)


class MobileAuthUserTestMixin(MobileAuthTestMixin):
    """
    Test Mixin for testing APIs related to users: mobile_view or MobileView with is_user=True.
    """
    def test_invalid_user(self):
        self.login_and_enroll()
        self.get_response(expected_response_code=403, username='no_user')

    def test_other_user(self):
        # login and enroll as the test user
        self.login_and_enroll()
        self.logout()

        # login and enroll as another user
        other = UserFactory.create()
        self.client.login(username=other.username, password='test')
        self.enroll()
        self.logout()

        # now login and call the API as the test user
        self.login()
        self.get_response(expected_response_code=403, username=other.username)


@ddt.ddt
class MobileCourseAccessTestMixin(object):
    """
    Test Mixin for testing APIs marked with mobile_course_access.
    (Use MobileEnrolledCourseAccessTestMixin when verify_enrolled is set to True.)
    Subclasses are expected to inherit from MobileAPITestCase.
    Subclasses can override verify_success, verify_failure, and init_course_access methods.
    """
    def verify_success(self, response):
        """Base implementation of verifying a successful response."""
        self.assertEqual(response.status_code, 200)

    def verify_failure(self, response):
        """Base implementation of verifying a failed response."""
        self.assertEqual(response.status_code, 404)

    def init_course_access(self, course_id=None):
        """Base implementation of initializing the user for each test."""
        self.login_and_enroll(course_id)

    def test_success(self):
        self.init_course_access()

        response = self.get_response(expected_response_code=None)
        self.verify_success(response)

    def test_course_not_found(self):
        non_existent_course_id = CourseKey.from_string('a/b/c')
        self.init_course_access(course_id=non_existent_course_id)

        response = self.get_response(expected_response_code=None, course_id=non_existent_course_id)
        self.verify_failure(response)

    @patch.dict('django.conf.settings.FEATURES', {'DISABLE_START_DATES': False})
    def test_unreleased_course(self):
        self.init_course_access()

        response = self.get_response(expected_response_code=None)
        self.verify_failure(response)

    @ddt.data(*ROLE_CASES)
    @ddt.unpack
    def test_non_mobile_available(self, role, should_succeed):
        self.init_course_access()

        # set mobile_available to False for the test course
        self.course.mobile_available = False
        self.store.update_item(self.course, self.user.id)

        # set user's role in the course
        if role:
            role(self.course.id).add_users(self.user)

        # call API and verify response
        response = self.get_response(expected_response_code=None)
        if should_succeed:
            self.verify_success(response)
        else:
            self.verify_failure(response)


class MobileEnrolledCourseAccessTestMixin(MobileCourseAccessTestMixin):
    """
    Test Mixin for testing APIs marked with mobile_course_access with verify_enrolled=True.
    """
    def test_unenrolled_user(self):
        self.login()
        self.unenroll()
        response = self.get_response(expected_response_code=None)
        self.verify_failure(response)


@ddt.ddt
class TestMobileApiUtils(MobileAPITestCase):
    """
    Tests for mobile API utilities
    """
    @ddt.data(*ROLE_CASES)
    @ddt.unpack
    def test_mobile_role_access(self, role, should_have_access):
        """
        Verifies that our mobile access function properly handles using roles to grant access
        """
        non_mobile_course = CourseFactory.create(mobile_available=False)
        if role:
            role(non_mobile_course.id).add_users(self.user)
        self.assertEqual(should_have_access, mobile_access_when_enrolled(non_mobile_course, self.user))

    def test_mobile_explicit_access(self):
        """
        Verifies that our mobile access function listens to the mobile_available flag as it should
        """
        self.assertTrue(mobile_access_when_enrolled(self.course, self.user))

    def test_missing_course(self):
        """
        Verifies that we handle the case where a course doesn't exist
        """
        self.assertFalse(mobile_access_when_enrolled(None, self.user))

    @patch.dict('django.conf.settings.FEATURES', {'DISABLE_START_DATES': False})
    def test_unreleased_course(self):
        """
        Verifies that we handle the case where a course hasn't started
        """
        self.assertFalse(mobile_access_when_enrolled(self.course, self.user))
