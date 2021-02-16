#
# PDF
# ---
# This script contains the
# class PDF
#
# Date: 2021-02-05
#
# Author: Lorenzo Coacci
#
#
# Copyright (C) 2021 Lorenzo Coacci
#
# pylint: disable=logging-format-interpolation,too-many-lines
#


# + + + + + Libraries + + + + +
# import basic
from golog.log import (
    error_print,
    warning_print,
    ask_password,
    list_print
)
from golog.tools import (
    correct_filepath,
    filepath_exists,
    to_int,
    correct_nonlist
)
# to manage pdfs
import PyPDF2
import tabula
import os
import ntpath
import uuid
import pandas as pd
# OCR
from pdf2image import convert_from_path
import cv2
from PIL import Image
import pyocr
import pyocr.builders
import pytesseract as pt
# + + + + + Libraries + + + + +


# + + + + + Classes + + + + +
# + + + + + PDF + + + + +
class PDF(object):
    def __init__(
        self,
        pdf_file_path,
        show_debug=False
    ):
        """Init and Load PDF file with PyPDF2"""
        # preprocessing checks
        pdf_file_path = str(pdf_file_path)
        if not filepath_exists(pdf_file_path):
            error_print(f"The file path {pdf_file_path} does not exist, please check again...")
            return

        # define
        self.mode = 'rb'
        self.pdf_file_path = pdf_file_path
        # (get also pdf file name)
        self.pdf_file_name = ntpath.basename(self.pdf_file_path).replace('.pdf', '')
        # open the file
        self.pdf_file = self.open_pdf(self.pdf_file_path, self.mode)
        # objects related
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file)
        # data
        self.num_pages = self.pdf_reader.numPages
        self.pages = [
            self.PDFPage(pdf=self, page_number=page, show_debug=show_debug)
            for page in range(self.num_pages)
        ]
        self.text = self.get_pdf_text()
        # is the PDF protected by a password?
        if self.is_encrypted():
            warning_print("This PDF is encrypted, please enter the password to decrypt it:\n\t>> ")
            password = ask_password()
            if password is None:
                error_print("Error: Problems while parsing your password")
                return
            result = self.pdf_reader.decrypt(password)
            if not bool(result):
                error_print("Could not decrypt your PDF, check your password and try again")
                return
        # debug
        self.show_debug = show_debug

    # + + + + + Inner Class - PDF Page + + + + +
    class PDFPage(object):
        def __init__(
            self, pdf, page_number, show_debug=False
        ):
            """Init and Load a PDF Page"""
            if page_number is None:
                raise ValueError("The Page Number cannot be None, please insert an integer, every PDFPage has an int reference to its PDF object")

            self.pdf = pdf
            self.num_pages = self.pdf.num_pages
            self.page_number = self._page_number_validated(page_number)
            # data
            self.pdf_page = self.pdf.pdf_reader.getPage(self.page_number)
            self.page_text = self.get_text()
            self.show_debug = show_debug

        def __repr__(self):
            return "<PDF Page [%s] >" % self.page_text[:10]
        
        def __int__(self):
            return len(self.page_text)
        
        def __len__(self):
            return len(self.page_text)
        
        def __hash__(self):
            return hash((self.page_text))

        def __eq__(self, other):
            if not isinstance(other, PDF):
                raise TypeError("Cannot compare a PDF Page object with a non PDF Page one")
            return self.__hash__() == other.__hash__()

        def __ne__(self, other):
            if not isinstance(other, PDF):
                raise TypeError("Cannot compare a PDF Page object with a non PDF Page one")
            return self.__hash__() != other.__hash__()

        def _page_number_validated(self, page_number):
            if not isinstance(page_number, int):
                page_number = to_int(page_number)
                if page_number is None:
                    error_print("The page number you input is not a int or not convertible to integer")
                    self._error_page_number_validation()
            if page_number < 0:
                if page_number < -(self.num_pages):
                    error_print(f"Cannot use the ngeative index with an abs number greater than the len {self.num_pages}")
                    self._error_page_number_validation()
                else:
                    page_number = self.num_pages + page_number
            elif page_number > self.num_pages:
                error_print(f"The Page of the number cannot be more than the max num of pages {self.num_pages}")
                self._error_page_number_validation()

            return page_number

        def get_text(self):
            return str(self.pdf_page.extractText())

        def export(self, output_file_path=None):
            # adding rotated page object to pdf writer
            writer = PyPDF2.PdfFileWriter()
            writer.addPage(self.pdf_page)
        
            # new pdf file object
            if output_file_path is None:
                to_replace = self.pdf.pdf_file_name
                output_file_path = self.pdf.pdf_file_path.replace(to_replace, to_replace + f'_page_{str(self.page_number)}')

            with open(output_file_path, 'wb') as new_file:
                # writing rotated pages to new file 
                writer.write(new_file)
    # + + + + + Inner Class - PDF Page + + + + +
    
    def to_pdf(self, output_file_path=None):
        writer = PyPDF2.PdfFileWriter()
        # writing a PDF object
        for page_number in range(self.num_pages):
            # copy in tmp file
            page = self.get_page(page_number).pdf_page
            # adding to file 
            writer.addPage(page)
        if output_file_path is None:
            output_file_path = self.pdf_file_path

        with open(output_file_path, 'wb') as new_file:
            # writing rotated pages to new file 
            writer.write(new_file) 

    def __enter__(self):
        return self.pdf

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Context Manager close PDF at the end"""
        self._close_file(self.pdf_file)

    def __repr__(self):
        return "<PDF File [%s] >" % self.text[:10]
    
    def __int__(self):
        return self.num_pages
    
    def __getitem__(self, page_number):
        return self.pages[page_number]
    
    def __len__(self):
        return self.num_pages

    def __add__(self, other):
        # pdf merge
        pdf_merger = PyPDF2.PdfFileMerger()
        pdf_merger.append(self.pdf_file)
        pdf_merger.append(other.pdf_file)

        to_replace = self.pdf_file_name
        output = self.pdf_file_path.replace(to_replace, f'{self.pdf_file_name}_{other.pdf_file_name}')

        # writing combined pdf to output pdf file 
        with open(output, 'wb') as f: 
            pdf_merger.write(f)

        # new file
        new_pdf = PDF(output)
        # delete file combined
        os.remove(output)

        return new_pdf
    
    def __hash__(self):
        return hash((self.num_pages, self.text))

    def __eq__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.__hash__() != other.__hash__()

    def __lt__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.num_pages < other.num_pages
    
    def __le__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.num_pages <= other.num_pages

    def __gt__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.num_pages > other.num_pages

    def __ge__(self, other):
        if not isinstance(other, PDF):
            raise TypeError("Cannot compare a PDF object with a non PDF one")
        return self.num_pages >= other.num_pages

    def open_pdf(self, file_path, mode):
        """Open a file"""
        return open(file_path, mode)
    
    def _close_file(self, file):
        """An internal way of closing files in general"""
        return file.close()
    
    def close(self):
        """Explicitly close the PDF class file when you are done"""
        return self.pdf_file.close()
    
    def get_number_of_pages(self):
        return self.pdf_reader.numPages

    def is_encrypted(self):
        return self.pdf_reader.isEncrypted

    def _error_page_number_validation(self):
        raise ValueError(
            "Validation Error while parsing the PDF page number (must be a int)"
        )

    def get_page(self, page_number):
        return self.pages[page_number]

    def get_page_text(self, page_number):
        return self.get_page(page_number).page_text

    def get_pdf_text(self):
        texts = [str(self.get_page_text(page_num)) for page_num in range(self.num_pages)]
        return ' '.join(texts)

    def get_pdf_tables(
        self, multiple_tables=True,
        area=None, pages=1,
        output_format=None
    ):
        df = tabula.read_pdf(
            self.pdf_file_path,
            area=area,
            pages=pages,
            output_format=output_format,
            multiple_tables=multiple_tables
        )
        return df

    def pdf_to_excel(self, excel_file_path):
        return tabula.convert_into(
            self.pdf_file_path,
            excel_file_path, output_format="xlsx"
        )

    def pdf_rotate(self, rotation, pages=None):
        # writing instance
        writer = PyPDF2.PdfFileWriter()
        if pages is None:
            pages = list(range(self.num_pages))
        else:
            # validate
            pages = correct_nonlist(pages)

        # rotating each page
        for page_number in range(self.num_pages):

            # creating rotated page object 
            page = self.get_page(page_number).pdf_page
            if page_number in pages:
                page.rotateClockwise(rotation)

            # adding rotated page object to pdf writer 
            writer.addPage(page) 
    
        # new pdf file object
        to_replace = self.pdf_file_name
        new_rotated_file_path = self.pdf_file_path.replace(to_replace, to_replace + '_rotated')
        
        with open(new_rotated_file_path, 'wb') as new_file:
            # writing rotated pages to new file 
            writer.write(new_file) 
    
        return True

    # - - - - - OCR - - - - -
    # ocr pdf to df
    def pdf_to_df(self, keep_page_images=False, ocr=None):
        """Convert a PDF to images then with OCR to data frame based on boxes (autodetected or not)"""
        available_ocrs = [
            'pyocr', 'pytesseract'
        ]
        ocr = 'pyocr' if ocr is None else ocr
        if ocr not in available_ocrs:
            error_print(f"This ocr {ocr} not available, only these ones {available_ocrs}")
            return None
        # convert to images
        jpgs = self.pdf_to_jpgs()
        if jpgs:
            df = None
            i = 1
            for jpg in jpgs:
                if ocr == 'pytesseract':
                    page_df = self.pytesseract_image_to_df(jpg)
                elif ocr == 'pyocr':
                    page_df = self.pyocr_image_to_df(jpg)
                else:
                    page_df = self.pyocr_image_to_df(jpg)
                page_df['page'] = i

                if keep_page_images:
                    self._image_auto_post_mark_regions(jpg, page_df, save_img=True)

                # remove image
                os.remove(jpg)
                
                # first df or not?
                if df is None:
                    df = page_df
                else:
                    df = df.append(page_df, ignore_index=True)
                
                i = i + 1

            return df
        else:
            error_print("Could not convert this PDF pages to images for the OCR process")
            return None

    # - PY OCR -
    def pyocr_get_tools(self):
        # all tools
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            warning_print("No OCR tool found")
            return None
        # The tools are returned in the recommended order of usage
        return {f"{t.get_name()}": t for t in tools}

    def pyocr_get_tool(self, tool_name):
        # all tools
        tools = self.pyocr_get_tools()
        tool = None
        if tools is not None:
            for t in tools:
                if t.get_name() == tool_name:
                    tool = t
                    break

        return tool

    def pyocr_get_tools_name(self):
        # all tools
        tools = self.pyocr_get_tools()
        if len(tools) == 0:
            warning_print("No OCR tool found")
            return None
        return [*map(lambda x: x.get_name(), tools)]
    
    def pyocr_get_tool_name(self, tool):
        # tool name
        return None if tool is None else tool.get_name()

    def pyocr_get_tool_languages(self, pyocr_tool):
        return pyocr_tool.get_available_languages()

    def pyocr_get_tool_language(self, tool, lang, default_eng=True):
        """Check if lang selected is available in the tool, if not default is english if default is applied"""
        langs = self.pyocr_get_tool_languages(tool)
        if lang in langs:
            pass
        else:
            warning_print(f"This language {lang} is not in the lang list for this tool")
            if default_eng:
                warning_print(f"Selecting eng as default if there . . .")
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    error_print(f"eng is not there as a lang!")
                    return None
        return lang
    
    def pyocr_image_to_text(self, image_path, tool=None, lang=None, broken_path_return_empty_txt=False):
        if tool is None:
            tool = self.pyocr_get_tools()["Tesseract (sh)"]
        if lang is None:
            lang = 'eng'

        image_path = str(image_path)
        if not filepath_exists(image_path):
            error_print(f"The image file path {image_path} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None

        txt = tool.image_to_string(
            Image.open(image_path),
            lang=str(lang),
            builder=pyocr.builders.TextBuilder()
        )
        return txt

    def pyocr_image_to_df(self, image_path, tool=None, lang=None, broken_path_return_empty_txt=False):
        if tool is None:
            tool = self.pyocr_get_tools()["Tesseract (sh)"]
        if lang is None:
            lang = 'eng'

        image_path = str(image_path)
        if not filepath_exists(image_path):
            error_print(f"The image file path {image_path} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None

        line_word_list = self.pyocr_image_to_line_and_boxes(
            image_path, tool=tool, lang=lang,
            broken_path_return_empty_txt=broken_path_return_empty_txt
        )

        # pass to a df
        df = pd.DataFrame(
            columns=[
                "line_uuid", "line_position", "line_content",
                "word_box_position", "word_box_content",
                "word_box_confidence"
            ]
        )
        for line in line_word_list:
            line_uuid = str(uuid.uuid4())
            line_position = line.get('position')
            line_content = line.get('content') 
            line_boxes = line.get('word_boxes')
            if line_boxes is None:
                df = df.append({
                        "line_uuid": line_uuid,
                        "line_position": line_position,
                        "line_content": line_content,
                        "word_box_position": None,
                        "word_box_content": None,
                        "word_box_confidence": None
                    }, ignore_index=True
                )
            else:
                for box in line_boxes:
                    df = df.append({
                            "line_uuid": line_uuid,
                            "line_position": line_position,
                            "line_content": line_content,
                            "word_box_position": box.get('position'),
                            "word_box_content": box.get('content'),
                            "word_box_confidence": box.get('confidence')
                        }, ignore_index=True
                    )

        return df

    def pyocr_image_to_boxes(self, image_path, tool=None, lang=None, broken_path_return_empty_txt=False):
        if tool is None:
            tool = self.pyocr_get_tools()["Tesseract (sh)"]
        if lang is None:
            lang = 'eng'

        image_path = str(image_path)
        if not filepath_exists(image_path):
            error_print(f"The image file path {image_path} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None

        word_boxes = tool.image_to_string(
            Image.open(image_path),
            lang=str(lang),
            builder=pyocr.builders.WordBoxBuilder()
        )
        return [{"position": box.position, "content": box.content, "confidence": box.confidence} for box in word_boxes]
    
    def pyocr_image_to_line_and_boxes(self, image_path, tool=None, lang=None, broken_path_return_empty_txt=False):
        if tool is None:
            tool = self.pyocr_get_tools()["Tesseract (sh)"]
        if lang is None:
            lang = 'eng'

        image_path = str(image_path)
        if not filepath_exists(image_path):
            error_print(f"The image file path {image_path} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None

        line_and_word_boxes = tool.image_to_string(
            Image.open(image_path),
            lang=str(lang),
            builder=pyocr.builders.LineBoxBuilder()
        )
        return [
            {
                "position": line.position,
                "content": line.content,
                "word_boxes": [{"position": box.position, "content": box.content, "confidence": box.confidence} for box in line.word_boxes]
            } for line in line_and_word_boxes
        ]

    def pyocr_image_to_digits(self, image_path, tool=None, lang=None, broken_path_return_empty_txt=False):
        if tool is None:
            tool = self.pyocr_get_tools()["Tesseract (sh)"]
        if lang is None:
            lang = 'eng'

        image_path = str(image_path)
        if not filepath_exists(image_path):
            error_print(f"The image file path {image_path} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None

        if 'Tesseract' not in tool.get_name():
            error_print("Other tools than Tesseract do not support image to digits")
            if broken_path_return_empty_txt:
                return ""
            return None

        digits = tool.image_to_string(
            Image.open(image_path),
            lang=str(lang),
            builder=pyocr.tesseract.DigitBuilder()
        )

        return digits
    # - PY OCR -

    # - PyTesseract -
    def pytesseract_image_to_df(self, image_path, lang=None, broken_path_return_empty_txt=False):
        if lang is None:
            lang = 'eng'

        if not filepath_exists(str(image_path)):
            error_print(f"The image file path {str(image_path)} does not exist, please check again...")
            if broken_path_return_empty_txt:
                return ""
            return None
        im = cv2.imread(str(image_path))

        df = pt.image_to_data(im, lang=lang, nice=0, output_type='data.frame')

        return df        
    # - PyTesseract -

    def pdf_to_jpgs(self, where=None, dpi=350, return_raw=False):
        """Convert each PDF page to a JPG image"""
        pages = convert_from_path(self.pdf_file_path, dpi=dpi)
        if where is None:
            where = self.pdf_file_path.replace('.pdf', '').replace(self.pdf_file_name, '')
        where = correct_filepath(where)
        if not pages:
            return []

        if return_raw:
            return pages

        i = 1
        paths = []
        for page in pages:
            image_name = f"{self.pdf_file_name}_page_" + str(i) + ".jpg"
            page.save(where + image_name, "JPEG")
            i = i + 1
            paths.append(where + image_name)
        
        return paths

    def _image_auto_post_mark_regions(self, image_path, page_df, save_img=False):
        # load image
        im = cv2.imread(image_path)

        box_positions = list(page_df['word_box_position'].values)
        line_items_coordinates = []
        for box in box_positions:
            #area = cv2.contourArea(c)
            #x, y, w, h = cv2.boundingRect(c)
            x, y = box[0]
            w, h = box[1]

            image = cv2.rectangle(im, (x, y), (2200, y + h), color=(255, 0, 255), thickness=3)
            line_items_coordinates.append([(x, y), (2200, y + h)])

        if save_img:
            image_name = ntpath.basename(image_path)
            if '.' in image_name:
                image_name = image_name.split('.')[0]
            self._save_image_from_array(image, image_path.replace(image_name, image_name + '_auto_post_marked'))

        return image, line_items_coordinates

    def _image_auto_pre_mark_regions(self, image_path, save_img=False):
        """Pre Auto Mark Boxes/Region for an image"""
        # from https://towardsdatascience.com/extracting-text-from-scanned-pdf-using-pytesseract-open-cv-cd670ee38052
        # load image
        im = cv2.imread(image_path)

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 30
        )

        # Dilate to combine adjacent text contours
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (9, 9)
        )
        dilate = cv2.dilate(thresh, kernel, iterations=4)

        # Find contours, highlight text areas, and extract ROIs
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        line_items_coordinates = []
        for c in cnts:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)

            if y >= 600 and x <= 1000:
                if area > 10000:
                    image = cv2.rectangle(im, (x, y), (2200, y + h), color=(255, 0, 255), thickness=3)
                    line_items_coordinates.append([(x, y), (2200, y + h)])

            if y >= 2400 and x <= 2000:
                image = cv2.rectangle(im, (x, y), (2200, y + h), color=(255, 0, 255), thickness=3)
                line_items_coordinates.append([(x, y), (2200, y + h)])

        if save_img:
            image_name = ntpath.basename(image_path)
            if '.' in image_name:
                image_name = image_name.split('.')[0]
            self._save_image_from_array(image, image_path.replace(image_name, image_name + '_auto_pre_marked'))

        return image, line_items_coordinates
    
    def _save_image_from_array(self, image, image_path):
        # save from array
        img = Image.fromarray(image, 'RGB')
        img.save(image_path)
        return image_path
    # - - - - - OCR - - - - -
# + + + + + PDF + + + + +
# + + + + + Classes + + + + +

# + + + + + Main + + + + +
if __name__ == "__main__":
    # Welcome!

    # - - PDF Init - -
    pdf_path = '/workspace/pdfer/test.pdf'
    pdf = PDF(pdf_path)

    # - - OCR - -
    df = pdf.pdf_to_df(
        keep_page_images=True,
        ocr='pyocr'
    )
    print(df)

    # try pytesseract
    df = pdf.pdf_to_df(
        ocr='pytesseract'
    )
    print(df)

# + + + + + Main + + + + +
