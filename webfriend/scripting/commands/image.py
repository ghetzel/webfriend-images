from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy
from PIL import Image
from PIL.ExifTags import TAGS
import io
import logging
import os
import pyocr
import pyocr.builders
from collections import OrderedDict
from unidecode import unidecode


def bbox2properties(bbox, rescale_factor=1.0):
    dest = OrderedDict()
    dest['bounding'] = OrderedDict()
    dest['bounding']['start'] = OrderedDict()
    dest['bounding']['start']['x'] = int(bbox[0][0] / rescale_factor)
    dest['bounding']['start']['y'] = int(bbox[0][1] / rescale_factor)
    dest['bounding']['end'] = OrderedDict()
    dest['bounding']['end']['x'] = int(bbox[1][0] / rescale_factor)
    dest['bounding']['end']['y'] = int(bbox[1][1] / rescale_factor)
    dest['width'] = dest['bounding']['end']['x'] - dest['bounding']['start']['x']
    dest['height'] = dest['bounding']['end']['y'] - dest['bounding']['start']['y']
    return dest


def postprocess_lines_boxes(list_of_lineboxen, text_handler=None, rescale_factor=1.0, **kwargs):
    out = []

    for linebox in list_of_lineboxen:
        line = OrderedDict()
        logging.debug(linebox.position)
        line.update(bbox2properties(linebox.position, rescale_factor=rescale_factor))

        line['words']  = postprocess_boxes(linebox.word_boxes, rescale_factor=rescale_factor)

        out.append(line)

    return out


def postprocess_boxes(list_of_boxen, text_handler=None, rescale_factor=1.0, **kwargs):
    if not len(list_of_boxen):
        return None

    out = []

    for box in list_of_boxen:
        text = box.content

        if text_handler:
            text = text_handler(text)

        word = OrderedDict()
        word['text']   = box.content
        word.update(bbox2properties(box.position, rescale_factor=rescale_factor))

        out.append(word)

    return out


def passthrough(value, text_handler=None, **kwargs):
    if text_handler:
        value = text_handler(value)

    return value


def text_asciify(value):
    if isinstance(value, str):
        value = value.encode('UTF-8')

    return unidecode(value).encode('UTF-8')


class ImageProxy(CommandProxy):
    """
    The `image` command set provides access to utiliies for loading, processing, and manipulating
    graphical data and for working with graphics primitives (like colors.)  These commands are
    useful for working with images on a webpage for tasks that include pixel color sampling and OCR
    text extraction.
    """

    pyocr_env_paths = {
        'TESSDATA_PREFIX': [
            '/usr/share/tessdata',
            '/usr/share/tesseract-ocr/tessdata',
        ],
    }

    # tuple format: name, pixel_format, bits, color count
    modes = {
        '1':     ('monochrome', 'B',     1,  2),
        'L':     ('greyscale',  'L',     8,  256),
        'P':     ('mapped',     'P',     8,  256),
        'RGB':   ('rgb',        'RGB',   8,  16777216),
        'RGBA':  ('rgba',       'RGBA',  8,  16777216),
        'CMYK':  ('cmyk',       'CMYK',  8,  16777216),
        'YCbCr': ('ycbcr',      'YCbCr', 8,  16777216),
        'LAB':   ('lab',        'LAB',   8,  16777216),
        'HSV':   ('hsv',        'HSV',   8,  16777216),
        'I':     ('opaque32',   'I',     32, 4294967296),
        'F':     ('opaque32f',  'F',     32, 4294967296),
    }

    def rgb2hex(self, r, g, b, a=None):
        """
        Converts an RGB[A] color value to hexadecimal.

        #### Arguments

        - **r**, **g**, **b**, **a** (`int`):

            The 8-bit integer values (0-255) of the red, green, blue, (and optionally) alpha
            components of the color to convert.

        #### Returns
        A string representing the hexadecimal color in the format `#RRGGBB` or `#RRGGBBAA`.
        """
        if a is not None:
            return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)
        else:
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def open(self, selector=None, url=None, file=None, attribute='src'):
        """
        Opens an image from a given local file, a file-like object, from a given URL, or from the
        image data referred to by the given HTML element.

        #### Arguments

        - **selector** (`str`, optional):

            A selector that refers to one and only one HTML element that has an attribute referring
            to an image that was loaded. This typically means selecting an `<img>` tag whose `src`
            attribute was used to load an image.

        - **url** (`str`, optional):

            If the URL of the image that was loaded is known directly, this is that URL.  This must
            be the URL of a request that has already occurred.

        - **file** (`str`, `file-like object`, optional):

            This is a file-like object or the string of a local filesystem file representing the
            image to load.

        - **attribute** (`str`):

            This is the attribute containing the image URL on the HTML element referred to by
            **selector**.

        #### Returns
        A raw image object that can be manipulated and queried.

        #### Raises
        - `ValueError` if none of the options were supplied.
        """
        image_resource = None

        if file:
            image_resource = file
        else:
            if selector:
                elements = self.tab.dom.select_nodes(selector, wait_for_match=True)
                element = self.tab.dom.ensure_unique_element(selector, elements)
                url = element[attribute]

            if url is None:
                raise ValueError(
                    "Must specify an element selector or request URL to retrieve image data from."
                )

            resource = self.tab.dom.get_resource(url=url)

            if resource and resource.get('completed'):
                image_resource = io.BytesIO()
                image_resource.write(self.tab.network.get_response_body(resource['id']))
                image_resource.seek(0)
            else:
                raise Exception("Failed to locate resource data for URL '{}'".format(url))

        return Image.open(image_resource)

    def info(self, selector=None, url=None, file=None, attribute='src'):
        """
        Retrieves details about an image.

        #### Arguments

        - **selector** (`str`, optional):

            A selector that refers to one and only one HTML element that has an attribute referring
            to an image that was loaded. This typically means selecting an `<img>` tag whose `src`
            attribute was used to load an image.

        - **url** (`str`, optional):

            If the URL of the image that was loaded is known directly, this is that URL.  This must
            be the URL of a request that has already occurred.

        - **file** (`str`, `file-like object`, optional):

            This is a file-like object or the string of a local filesystem file representing the
            image to load.

        - **attribute** (`str`):

            This is the attribute containing the image URL on the HTML element referred to by
            **selector**.

        #### Returns
        A `dict` containing image details.

        - *width*, *height* (`int`):

            The width and height of the image in pixels.

        - *mode* (`str`):

            The type of palette this image has.

        - *colors* (`int`):

            The number of colors this image palette can represent.

        - *bitdepth* (`int`):

            The number of bits used to represent individual color components.

        - *pixel_format* (`str`):

            A string representing the number and order of color components.

        - *bits_per_pixel* (`int`):

            The number of bits used to represent each pixel.

        - *exif* (`dict`, optional):

            If available, this will contain any EXIF data embedded in the image.
        """
        image = self.open(selector=selector, url=url, file=file, attribute=attribute)

        mode = image.mode
        mode_name = None
        bitdepth = None
        colors = None
        pixel_format = None

        if mode in self.modes:
            mode_name, pixel_format, bitdepth, colors = self.modes[mode]

        data = OrderedDict()
        data['width']         = image.width
        data['height']        = image.height
        data['mode']          = mode_name
        data['colors']        = colors
        data['bitdepth']      = bitdepth
        data['pixel_format']  = pixel_format
        data['extended_info'] = image.info

        if bitdepth and pixel_format:
            data['bits_per_pixel'] = (bitdepth * len(pixel_format))

        # populate EXIF data (if present)
        try:
            for tag, value in image._getexif().items():
                if 'exif' not in data:
                    data['exif'] = {}

                data['exif'][tag] = TAGS.get(tag, tag)

        except AttributeError:
            pass

        return data

    def extract_text(
        self,
        selector=None,
        url=None,
        file=None,
        attribute='src',
        language='eng',
        output_format='raw',
        text_to_ascii=True,
        rescale_factor=2.0,
        rescale_width_threshold=4160
    ):
        """
        Attempts to determine the text content of an image using OCR processing.

        #### Arguments

        - **selector** (`str`, optional):

            A selector that refers to one and only one HTML element that has an attribute referring
            to an image that was loaded. This typically means selecting an `<img>` tag whose `src`
            attribute was used to load an image.

        - **url** (`str`, optional):

            If the URL of the image that was loaded is known directly, this is that URL.  This must
            be the URL of a request that has already occurred.

        - **file** (`str`, `file-like object`, optional):

            This is a file-like object or the string of a local filesystem file representing the
            image to load.

        - **attribute** (`str`):

            This is the attribute containing the image URL on the HTML element referred to by
            **selector**.

        - **language** (`str`):

            The language of the text that is being detected.

        - **output_format** (`str`):

            Describes the way the text content is expected to be presented within the image.
            Changing this value can help to refine the text extraction process and help improve
            result accuracy.  Valid values include:

            - *raw* (default):

                Attempt to extract any text that is located in the image in the order that it is
                encountered.  This is a good option for arbitrary images where little is known
                about how the text is likely to be presented, with the trade-off that accuracy will
                suffer as a result (mismatched or unmatched text is more likely.)

            - *numeric*:

                Treat the incoming image as only containing digits.

            - *numeric-words*:

                Treat the incoming image as only containing digits separated into separate "words"
                by whitespace or non-numeric characters (e.g.: phone numbers, social security
                numbers, etc.)  Output will be a list of objects describing each recognized
                sequence of numbers, along with the position and dimensions of those words in the
                source image.

            - *lines*:

                Return recognized text as a list of objects describing individual lines of
                recognized text.

        - **text_to_ascii** (`bool`):

            Whether to automatically convert the resulting text to the ASCII character set before
            returning. This is useful as the OCR process often produces output that includes
            unusual characters not typically found in the source language because, due to various
            quirks inherent in the underlying OCR models, those glyphs were deemed a better match
            optically-speaking.

            This serves to undo that and provide a better fit for languages with Latin-based
            alphabets.

        - **rescale_factor** (`float`):

            The underlying OCR process works MUCH better with larger input images, so this provides
            some tuning for resizing the input image data to potentially produce better results.
            The default is to double the image size provided the input image's width is less than
            **rescale_width_threshold**.

        - **rescale_width_threshold** (`int`):

            For **rescale_factor** values greater than 1.0, this represents the maximum width of an
            input image for which the rescale will occur (e.g.: don't blow up images that are
            already large to begin with.)

            For **rescale_factor** values less than 1.0, this is the _minumum_ width of an input
            image below which it doesn't make sense to shrink it further.  Factor's less than 1.0
            only really make sense in the context of OCR extraction when the source images are VERY
            large and you want to discard some data and save time or memory during processing.

        #### Returns
        A string representing the detected text, or `None` if the detection failed.
        """
        image = self.open(selector=selector, url=url, file=file, attribute=attribute)

        # Tesseract will have a much better time with larger images, so as a safety margin we're
        # going to double the size of any input image that's narrower than rescale_width_threshold.
        #
        # Unless we're trying to make the image smaller, in which case rescale_width_threshold is
        # interpreted to mean "maximum size".
        #
        if rescale_factor < 1.0 and image.width > rescale_width_threshold or \
           rescale_factor > 1.0 and image.width < rescale_width_threshold:
            size = (int(image.width * rescale_factor), int(image.height * rescale_factor))

            logging.debug('Resizing image ({} x {}) {}x to ({} x {})'.format(
                image.width,
                image.height,
                rescale_factor,
                size[0],
                size[1]
            ))

            image = image.resize(
                size,
                resample=Image.BICUBIC
            )

        tools = pyocr.get_available_tools()

        if not len(tools):
            raise Exception("No OCR tools available")

        for tool in tools:
            for env, values in self.pyocr_env_paths.items():
                for value in values:
                    os.environ[env] = value

                    try:
                        languages = tool.get_available_languages()

                        if language in languages:
                            ocr_lang = languages[languages.index(language)]
                        else:
                            continue

                        postprocess = passthrough
                        text_handler = None

                        if text_to_ascii:
                            text_handler = text_asciify

                        # Text Builders
                        # -------------
                        if output_format == 'raw':
                            builder = pyocr.builders.TextBuilder()

                        elif output_format == 'numeric':
                            builder = pyocr.builders.DigitBuilder()

                        elif output_format == 'numeric-words':
                            builder = pyocr.builders.DigitLineBoxBuilder()
                            postprocess = postprocess_boxes

                        elif output_format == 'words':
                            builder = pyocr.builders.WordBoxBuilder()
                            postprocess = postprocess_boxes

                        elif output_format == 'lines':
                            builder = pyocr.builders.LineBox()
                            postprocess = postprocess_boxes

                        elif output_format == 'lines-words':
                            builder = pyocr.builders.LineBoxBuilder()
                            postprocess = postprocess_lines_boxes

                        elif output_format == 'characters':
                            builder = pyocr.tesseract.CharBoxBuilder()
                            postprocess = postprocess_boxes

                        else:
                            raise ValueError("Unrecognized output_format '{}'".format(
                                output_format
                            ))

                        logging.debug('Performing character recognition on input image')

                        return postprocess(tool.image_to_string(
                            image,
                            lang=ocr_lang,
                            builder=builder
                        ), text_handler=text_handler, rescale_factor=rescale_factor)

                    except:
                        continue

        return None

    def pixel(self, selector=None, url=None, file=None, attribute='src', x=None, y=None):
        """
        Retrieves the color of a specific pixel in the image.

        #### Arguments

        - **selector** (`str`, optional):

            A selector that refers to one and only one HTML element that has an attribute referring
            to an image that was loaded. This typically means selecting an `<img>` tag whose `src`
            attribute was used to load an image.

        - **url** (`str`, optional):

            If the URL of the image that was loaded is known directly, this is that URL.  This must
            be the URL of a request that has already occurred.

        - **file** (`str`, `file-like object`, optional):

            This is a file-like object or the string of a local filesystem file representing the
            image to load.

        - **attribute** (`str`):

            This is the attribute containing the image URL on the HTML element referred to by
            **selector**.

        - **x**, **y** (`int`):

            The X,Y coordinates (relative to the top-left corner of the image) of the pixel to
            retrieve.

        #### Returns
        A `dict` containing the integer values of each color component of the pixel, and the key
        *hex* with a string representing the hexadecimal value of the pixel.
        """
        image = self.open(selector=selector, url=url, file=file, attribute=attribute)

        if x is None or y is None:
            raise ValueError("Must specify both x and y values")

        if image.mode in self.modes:
            _, pixel_format, _, _ = self.modes[image.mode]

            pixel_data = OrderedDict()
            values = image.getpixel((x, y))

            # make sure the pixel format and returned value count matches
            if len(pixel_format) == len(values):
                # add all colors to the result
                for i, color in enumerate(pixel_format):
                    pixel_data[color.lower()] = values[i]

                # populate the hexadecimal value
                if pixel_format == 'RGB':
                    pixel_data['hex'] = self.rgb2hex(values[0], values[1], values[2])
                elif pixel_format == 'RGBA':
                    pixel_data['hex'] = self.rgb2hex(values[0], values[1], values[2], values[3])

                return pixel_data
            else:
                raise Exception("Pixel value count does not match pixel format")
        else:
            raise Exception("Unknown pixel format")
