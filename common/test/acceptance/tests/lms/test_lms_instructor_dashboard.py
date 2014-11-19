# -*- coding: utf-8 -*-
"""
End-to-end tests for the LMS Instructor Dashboard.
"""

from ..helpers import UniqueCourseTest
from ...pages.lms.auto_auth import AutoAuthPage
from ...pages.lms.instructor_dashboard import InstructorDashboardPage
from ...pages.lms.instructor_dashboard_paid_course_registrations import AddHonorModeToCoursePage
from ...fixtures.course import CourseFixture


class AutoEnrollmentWithCSVTest(UniqueCourseTest):
    """
    End-to-end tests for Auto-Registration and enrollment functionality via CSV file.
    """

    def setUp(self):
        super(AutoEnrollmentWithCSVTest, self).setUp()
        self.course_fixture = CourseFixture(**self.course_info).install()

        # login as an instructor
        AutoAuthPage(self.browser, course_id=self.course_id, staff=True).visit()

        # go to the membership page on the instructor dashboard
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        self.auto_enroll_section = instructor_dashboard_page.select_membership().select_auto_enroll_section()

    def test_browse_and_upload_buttons_are_visible(self):
        """
        Scenario: On the Membership tab of the Instructor Dashboard, Auto-Enroll Browse and Upload buttons are visible.
            Given that I am on the Membership tab on the Instructor Dashboard
            Then I see the 'REGISTER/ENROLL STUDENTS' section on the page with the 'Browse' and 'Upload' buttons
        """
        self.assertTrue(self.auto_enroll_section.is_file_attachment_browse_button_visible())
        self.assertTrue(self.auto_enroll_section.is_upload_button_visible())

    def test_clicking_file_upload_button_without_file_shows_error(self):
        """
        Scenario: Clicking on the upload button without specifying a CSV file results in error.
            Given that I am on the Membership tab on the Instructor Dashboard
            When I click the Upload Button without specifying a CSV file
            Then I should be shown an Error Notification
            And The Notification message should read 'File is not attached.'
        """
        self.auto_enroll_section.click_upload_file_button()
        self.assertTrue(self.auto_enroll_section.is_notification_displayed(section_type=self.auto_enroll_section.NOTIFICATION_ERROR))
        self.assertEqual(self.auto_enroll_section.first_notification_message(section_type=self.auto_enroll_section.NOTIFICATION_ERROR), "File is not attached.")

    def test_uploading_correct_csv_file_results_in_success(self):
        """
        Scenario: Uploading a CSV with correct data results in Success.
            Given that I am on the Membership tab on the Instructor Dashboard
            When I select a csv file with correct data and click the Upload Button
            Then I should be shown a Success Notification.
        """
        self.auto_enroll_section.upload_correct_csv_file()
        self.assertTrue(self.auto_enroll_section.is_notification_displayed(section_type=self.auto_enroll_section.NOTIFICATION_SUCCESS))

    def test_uploading_csv_file_with_bad_data_results_in_errors_and_warnings(self):
        """
        Scenario: Uploading a CSV with incorrect data results in error and warnings.
            Given that I am on the Membership tab on the Instructor Dashboard
            When I select a csv file with incorrect data and click the Upload Button
            Then I should be shown an Error Notification
            And a corresponding Error Message.
            And I should be shown a Warning Notification
            And a corresponding Warning Message.
        """
        self.auto_enroll_section.upload_csv_file_with_errors_warnings()
        self.assertTrue(self.auto_enroll_section.is_notification_displayed(section_type=self.auto_enroll_section.NOTIFICATION_ERROR))
        self.assertEqual(self.auto_enroll_section.first_notification_message(section_type=self.auto_enroll_section.NOTIFICATION_ERROR), "Data in row #2 must have exactly four columns: email, username, full name, and country")
        self.assertTrue(self.auto_enroll_section.is_notification_displayed(section_type=self.auto_enroll_section.NOTIFICATION_WARNING))
        self.assertEqual(self.auto_enroll_section.first_notification_message(section_type=self.auto_enroll_section.NOTIFICATION_WARNING), "ename (d@a.com): (An account with email d@a.com exists but the provided username ename is different. Enrolling anyway with d@a.com.)")

    def test_uploading_non_csv_file_results_in_error(self):
        """
        Scenario: Uploading an image file for auto-enrollment results in error.
            Given that I am on the Membership tab on the Instructor Dashboard
            When I select an image file (a non-csv file) and click the Upload Button
            Then I should be shown an Error Notification
            And The Notification message should read 'Make sure that the file you upload is in CSV..'
        """
        self.auto_enroll_section.upload_non_csv_file()
        self.assertTrue(self.auto_enroll_section.is_notification_displayed(section_type=self.auto_enroll_section.NOTIFICATION_ERROR))
        self.assertEqual(self.auto_enroll_section.first_notification_message(section_type=self.auto_enroll_section.NOTIFICATION_ERROR), "Make sure that the file you upload is in CSV format with no extraneous characters or rows.")


class ECommerceCouponsListTest(UniqueCourseTest):
    """
    End-to-end tests for Coupon Codes in E-Commerce Section of the Instructor Dashboard.
    """

    def setUp(self):
        super(ECommerceCouponsListTest, self).setUp()

        # setup a course.
        self.course_fixture = CourseFixture(**self.course_info).install()

        # login as an instructor
        AutoAuthPage(self.browser, course_id=self.course_id, staff=True).visit()

        # Convert the course to a Paid Course Registration
        AddHonorModeToCoursePage(self.browser, self.course_id).visit()

        # go to the coupons list on the E-Commerce section of the instructor dashboard
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()

        # Select the Coupons Section
        self.coupons_list_section = instructor_dashboard_page.select_ecommerce().select_coupons_list()

    def test_download_and_add_buttons_are_visible(self):
        """
        Scenario: Buttons are present to download and add Coupons.
        Given that I am on the on the Coupons Section of the E-Commerce tab of the Instructor Dashboard
        Then I see the 'COUPONS LIST' section on the page with the 'Download coupon codes' and 'Add Coupon' buttons.
        """
        self.assertTrue(self.coupons_list_section.is_download_button_visible())
        self.assertTrue(self.coupons_list_section.is_add_button_visible())

    def test_required_fields_are_present_on_popup(self):
        """
        Scenario: Clicking on the "Add Coupon" button shows a popup with the required fields.
        Given that I am on the on the Coupons Section of the E-Commerce tab of the Instructor Dashboard
        When I click the "Add Coupon" button.
        Then I can see a popup with the fields to create a coupon.
        """
        self.coupons_list_section.click_to_show_add_coupon_popup()
        self.assertTrue(self.coupons_list_section.required_fields_are_visible_on_popup())

    def test_can_add_a_coupon_without_expiry_date(self):
        """
        Scenario: The user can add a coupon without an expiry date.
        Given that I am on the on the Coupons Section of the E-Commerce tab of the Instructor Dashboard
        When I click the "Add Coupon" button
        And I enter all fields except the expiry date
        And click on the Add Coupon submit button
        Then a new coupon without an expiry date is successfully added.
        """
        self.coupons_list_section.click_to_show_add_coupon_popup()
        self.coupons_list_section.set_data_on_add_coupon_popup_and_submit(coupon_code="ABC123", discount="10", description="test")

        # The page reloaded. Navigate to the page again.
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        self.coupons_list_section = instructor_dashboard_page.select_ecommerce().select_coupons_list()

        self.assertTrue(self.coupons_list_section.compare_row_data(coupon_code="ABC123", discount="10", description="test", expiration_date="None", was_expired=False))

    def test_can_add_a_coupon_with_expiry_date(self):
        """
        Scenario: The user can add a coupon with an expiry date.
        Given that I am on the on the Coupons Section of the E-Commerce tab of the Instructor Dashboard
        When I click the "Add Coupon" button
        And I enter all fields including the expiry date
        And click on the Add Coupon submit button
        Then a new coupon with an expiry date is successfully added.
        """
        self.coupons_list_section.click_to_show_add_coupon_popup()
        self.coupons_list_section.set_data_on_add_coupon_popup_and_submit(coupon_code="ABC1234", discount="10", description="test", expiration_date="11/27/2999")

        # The page reloaded. Navigate to the page again.
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        self.coupons_list_section = instructor_dashboard_page.select_ecommerce().select_coupons_list()

        self.assertTrue(self.coupons_list_section.compare_row_data(coupon_code="ABC1234", discount="10", description="test", expiration_date="November 27, 2999", was_expired=False))

    def test_expired_coupons_show_up_in_yellow(self):
        """
        Scenario: Expired coupons show up with a yellow background.
        Given that I am on the on the Coupons Section of the E-Commerce tab of the Instructor Dashboard
        When I click the "Add Coupon" button
        And I enter all fields with an expiry date in the past
        And click on the Add Coupon submit button
        Then a new coupon with an expiry date is successfully added
        And it is shown in yellow background.
        """
        self.coupons_list_section.click_to_show_add_coupon_popup()
        self.coupons_list_section.set_data_on_add_coupon_popup_and_submit(coupon_code="ABC12345", discount="10", description="test", expiration_date="11/27/2000")

        # The page reloaded. Navigate to the page again.
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        self.coupons_list_section = instructor_dashboard_page.select_ecommerce().select_coupons_list()

        self.assertTrue(self.coupons_list_section.compare_row_data(coupon_code="ABC12345", discount="10", description="test", expiration_date="November 27, 2000", was_expired=True))
