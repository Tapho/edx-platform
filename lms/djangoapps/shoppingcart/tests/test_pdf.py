"""
Tests for Pdf file
"""
from datetime import datetime
from django.test.utils import override_settings
import unittest
from io import BytesIO
from shoppingcart.pdf import PDFInvoice
from django.core.files import File


class TestPdfFile(unittest.TestCase):
    """
    Unit test cases for pdf file generation
    """
    def setUp(self):
        self.context = {
            'items_data': [self.get_item_data(1)],
            'id': str(1),
            'date': datetime.now(),
            'is_invoice': False,
            'total_cost': 1000,
            'payment_received': 1000,
            'balance': 0,
        }
        self.pdf_buffer = BytesIO()

    def get_item_data(self, index, discount=0):
        """
        return the dictionary with the dummy data
        """
        return {
            'item_description': 'Course %s Description' % index,
            'quantity': index,
            'list_price': 10,
            'discount': discount,
            'item_total': 10
        }

    def test_pdf_generation(self):
        PDFInvoice(self.context).generate_pdf(self.pdf_buffer)
        # with open('/edx/app/edxapp/edx-platform/receipt.pdf', 'w') as f:
        #     myfile = File(f)
        #     myfile.write(self.pdf_buffer.getvalue())

    def test_pdf_file_item_data_pagination(self):
        for i in range(2, 50):
            self.context['items_data'].append(self.get_item_data(i))

        PDFInvoice(self.context).generate_pdf(self.pdf_buffer)

    def test_pdf_file_totals_pagination(self):
        for i in range(2, 48):
            self.context['items_data'].append(self.get_item_data(i))

        PDFInvoice(self.context).generate_pdf(self.pdf_buffer)

    @override_settings(PDF_RECEIPT_LOGO_PATH='wrong path')
    def test_invalid_image_path(self):
        PDFInvoice(self.context).generate_pdf(self.pdf_buffer)

    def test_pdf_file_footer_pagination(self):
        for i in range(2, 42):
            self.context['items_data'].append(self.get_item_data(i))

        PDFInvoice(self.context).generate_pdf(self.pdf_buffer)
