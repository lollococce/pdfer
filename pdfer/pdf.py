"""
PDF
---
This script contains the
class PDF

Date: 2021-02-05

Author: Lorenzo Coacci
"""
# + + + + + Libraries + + + + +
# import basic
from golog.log import (
    error_print
)
from golog.tools import (
    correct_filepath,
    filepath_exists
)
# to manage pdfs
import PyPDF2
# + + + + + Libraries + + + + +


# + + + + + Classes + + + + +
# + + + + + PDF + + + + +
class PDF:
    def __init__(
        self,
        pdf_file_path,
        show_debug=False
    ):
        # Init
        pdf_file_path = str(pdf_file_path)
        if not filepath_exists(pdf_file_path):
            error_print(f"The file path {pdf_file_path} does not exist, please check again...")
            return
        pdf_file = open(pdf_file_path, 'rb')
        self.pdf = PyPDF2.PdfFileReader(pdf_file)
        self.num_pages = self.pdf.numPages
        self.show_debug = show_debug

    def get_all_text(self):
        texts = [str(self.pdf.getPage(page).extractText()) for page in range(self.num_pages)]
        return ' '.join(texts)
    
    def get_text_page_x(self, page_num_x):
        if page_num_x < 0 or page_num_x <= self.num_pages:
            error_print(f"The Page of the number cannot be less than 0 or more than the max num of pages {self.num_pages}")
            return None
        elif page_num_x == 0:
            page_num_x = 1
        return str(self.pdf.getPage(page_num_x - 1).extractText())
# + + + + + PDF + + + + +
# + + + + + Classes + + + + +


if __name__ == "__main__":
    print(correct_filepath('gfghjkllkjh/ghjk'))

    pdf = PDF('/Users/lorenzo/Desktop/test.pdf')

    print(pdf.get_all_text)