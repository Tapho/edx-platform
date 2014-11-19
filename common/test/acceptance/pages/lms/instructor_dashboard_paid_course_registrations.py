# -*- coding: utf-8 -*-
"""
Instructor Dashboard Page for Paid Course Registrations.
"""

from bok_choy.page_object import PageObject
from ...fixtures import LMS_BASE_URL


class AddHonorModeToCoursePage(PageObject):
    """
    PageObject to add Honor Mode to a given course to make it a Paid Course Registration.
    """

    def __init__(self, browser, course_id):

        super(AddHonorModeToCoursePage, self).__init__(browser)

        # Create query string parameters if provided
        self.course_id = course_id

    @property
    def url(self):
        """
        Construct the URL with the Query parameter (course ID) to send to the API
        """
        url = LMS_BASE_URL + "/course_modes/add_mode_to_course/%s" % self.course_id
        return url

    def is_browser_on_page(self):
        self.wait_for_element_presence('.add-course-mode #add_course_mode_form', 'Add Course Mode Form')
        self.q(css="form input[name='course_mode']").results[0].send_keys('honor')
        self.q(css="form input[name='course_mode_display_name']").results[0].send_keys('honor')
        self.q(css="form input[name='course_mode_price']").results[0].send_keys('100')
        self.q(css="form input[name='course_mode_currency']").results[0].send_keys('usd')
        self.q(css=".add-course-mode #add_course_mode_form input[type='submit']").click()

        self.wait_for_element_absence('.add-course-mode #add_course_mode_form', "Add Course Mode Form removed from the success page.")
        self.wait_for_element_presence('body', 'body')
        response_text = self.q(css='body').first.text[0]
        return response_text == "success"


class ECommercePage(PageObject):
    """
    E-Commerce tab of the Instructor dashboard.
    """
    url = None
    coupons_list_accordion_selector = '.ecommerce-wrapper div.wrap:last-child'

    def is_browser_on_page(self):
        return self.q(css='a[data-section=e-commerce].active-section').present

    def select_coupons_list(self):
        """
        returns the ECommercePageCouponsListSection
        """
        ecommerce_page_coupons_list = ECommercePageCouponsListSection(self.browser)
        if not ecommerce_page_coupons_list.is_browser_on_page():
            self.q(css=self.coupons_list_accordion_selector).click()
        ecommerce_page_coupons_list.wait_for_page()
        return ecommerce_page_coupons_list


class ECommercePageCouponsListSection(PageObject):
    """
    Coupons list section on the E-Commerce section of the Instructor Dashboard.
    """
    url = None
    download_coupon_codes_selector = ".ecommerce-wrapper div[aria-expanded='true'] input[name='download-coupon-codes-csv']"
    add_coupon_selector = '.ecommerce-wrapper div[aria-expanded="true"] #add_coupon_link'

    def is_browser_on_page(self):
        return self.q(css=self.add_coupon_selector).present

    def is_download_button_visible(self):
        """
        Returns True if the Download coupon codes button is present.
        """
        return self.q(css=self.download_coupon_codes_selector).is_present()

    def is_add_button_visible(self):
        """
        Returns True if the Add Coupon button is present.
        """
        return self.q(css=self.add_coupon_selector).is_present()

    def click_to_show_add_coupon_popup(self):
        """
        Clicks the "Add Coupon" button to bring up a popup.
        """
        self.q(css="#djHideToolBarButton").click()
        self.q(css=self.add_coupon_selector).click()

        # wait for modal to appear.
        self.wait_for_element_presence('#add-coupon-modal[style*="display: block"]', 'add coupon popup')

    def is_coupon_code_field_present(self):
        """
        Return True if the coupon code field is present on the Add Coupon Popup
        """
        return self.q(css="#coupon_code").is_present()

    def is_coupon_discount_field_present(self):
        """
        Return True if the Discount field is present on the Add Coupon Popup
        """
        return self.q(css="#coupon_discount").is_present()

    def is_coupon_description_field_present(self):
        """
        Return True if the Description field is present on the Add Coupon Popup
        """
        return self.q(css="#coupon_description").is_present()

    def is_coupon_expiration_checkbox_present(self):
        """
        Return True if the Expiration checkbox is present on the Add Coupon Popup
        """
        return self.q(css="#expiry-check").is_present()

    def click_coupon_expiration_checkbox(self):
        """
        Clicks the Expiry Date checkbox
        """
        self.q(css="#expiry-check").click()
        self.wait_for_element_presence("#coupon_expiration_date", "expiry textbox")

    def is_expiry_date_field_hidden_when_checkbox_unchecked(self):
        """
        Return True if the Expiry Date field is hidden on the Add Coupon Popup
        """
        return self.q(css='#coupon_expiration_date[style*="display: none"]').is_present()

    def is_expiry_date_field_present_when_checkbox_checked(self):
        """
        Return True if the Expiry Date field is visible on the Add Coupon Popup
        """
        self.click_coupon_expiration_checkbox()
        return self.q(css='#coupon_expiration_date[style*="display: block"]').is_present()

    def is_submit_coupon_button_present(self):
        """
        Return True if the Add Coupon submit button is present on the Add Coupon Popup
        """
        return self.q(css="#add_coupon_button").is_present()

    def required_fields_are_visible_on_popup(self):
        """
        Return True if all the required fields (code, discount, description, expiration date, and submit button) are
        visible on the popup.
        """
        if not self.is_coupon_code_field_present():
            return False
        if not self.is_coupon_discount_field_present():
            return False
        if not self.is_coupon_description_field_present():
            return False
        if not self.is_coupon_expiration_checkbox_present():
            return False
        if not self.is_expiry_date_field_hidden_when_checkbox_unchecked():
            return False
        if not self.is_expiry_date_field_present_when_checkbox_checked():
            return False
        if not self.is_submit_coupon_button_present():
            return False

        return True

    def set_data_on_add_coupon_popup_and_submit(self, coupon_code, discount, description, expiration_date=None):
        """
        Fills the Add Coupon popup with the respective values.
        """
        self.q(css="#coupon_code").results[0].send_keys(coupon_code)
        self.q(css="#coupon_discount").results[0].send_keys(discount)
        self.q(css="#coupon_description").results[0].send_keys(description)

        if expiration_date:
            self.click_coupon_expiration_checkbox()
            self.q(css="#coupon_expiration_date").results[0].send_keys(expiration_date)

        self.q(css="#coupon_discount").click()  # clicking somewhere else to hide the calendar.
        self.q(css="#add_coupon_button").click()

        # wait for data row to appear
        self.wait_for_element_presence('table.coupons-table tbody tr:nth-child(1)', "coupon row in table.")

    def compare_row_data(self, coupon_code, discount, description, was_expired=False, expiration_date=None):
        """
        Compares the submitted data with the displayed list of coupons.
        """
        selector = "table.coupons-table tr.coupons-items{expired}:nth-child(1) td:nth-child({column})"

        expired_selector = ".expired_coupon" if was_expired else ""

        table_coupon_code = self.q(css=selector.format(expired=expired_selector, column=1)).first.text[0]
        if table_coupon_code != coupon_code:
            return False

        table_coupon_description = self.q(css=selector.format(expired=expired_selector, column=2)).first.text[0]
        if table_coupon_description != description:
            return False

        table_coupon_expiry = self.q(css=selector.format(expired=expired_selector, column=3)).first.text[0]
        if expiration_date and table_coupon_expiry != expiration_date:
            return False

        table_coupon_discount = self.q(css=selector.format(expired=expired_selector, column=4)).first.text[0]
        if table_coupon_discount != discount:
            return False

        return True
