from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy
from PIL import Image
from PIL.ExifTags import TAGS
import io
import os
import pyocr
import pyocr.builders
from collections import OrderedDict


class ImageProxy(CommandProxy):
    pyocr_env_paths = {
        'TESSDATA_PREFIX': [
            '/usr/share/tessdata',
            '/usr/share/tesseract-ocr/tessdata',
        ],
    }

    # tuple format: name, pixel_format, bits, color count

    # 1 (1-bit pixels, black and white, stored with one pixel per byte)
    # L (8-bit pixels, black and white)
    # P (8-bit pixels, mapped to any other mode using a color palette)
    # RGB (3x8-bit pixels, true color)
    # RGBA (4x8-bit pixels, true color with transparency mask)
    # CMYK (4x8-bit pixels, color separation)
    # YCbCr (3x8-bit pixels, color video format)
    # LAB (3x8-bit pixels, the L*a*b color space)
    # HSV (3x8-bit pixels, Hue, Saturation, Value color space)
    # I (32-bit signed integer pixels)
    # F (32-bit floating point pixels)

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

        data = {
            'width':        image.width,
            'height':       image.height,
            'mode':         mode_name,
            'colors':       colors,
            'bitdepth':     bitdepth,
            'pixel_format': pixel_format,
        }

        if bitdepth and pixel_format:
            data['bits_per_pixel'] = (bitdepth * len(pixel_format))

        # populate EXIF data (if present)
        for tag, value in image._getexif().items():
            if 'exif' not in data:
                data['exif'] = {}

            data['exif'][tag] = TAGS.get(tag, tag)

        return data

    def extract_text(self, selector=None, url=None, file=None, attribute='src', language='eng'):
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

        #### Returns
        A string representing the detected text, or `None` if the detection failed.
        """
        image = self.open(selector=selector, url=url, file=file, attribute=attribute)

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

                        return tool.image_to_string(
                            image,
                            lang=ocr_lang,
                            builder=pyocr.builders.TextBuilder()
                        )

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
