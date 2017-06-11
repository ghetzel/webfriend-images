# Command Reference
- [Image](#image-command-set)
   - **[image::extract_text](#imageextract_text)**
   - **[image::info](#imageinfo)**
   - **[image::open](#imageopen)**
   - **[image::pixel](#imagepixel)**
   - **[image::rgb2hex](#imagergb2hex)**

## `image` Command Set

The `image` command set provides access to utiliies for loading, processing, and manipulating
graphical data and for working with graphics primitives (like colors.)  These commands are
useful for working with images on a webpage for tasks that include pixel color sampling and OCR
text extraction.

### `image::extract_text`

```
image::extract_text <SELECTOR> {
    url:                     null,
    file:                    null,
    attribute:               'src',
    language:                'eng',
    output_format:           'raw',
    text_to_ascii:           true,
    rescale_factor:          2.0,
    rescale_width_threshold: 4160
}
```

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

---

### `image::info`

```
image::info <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src'
}
```

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

---

### `image::open`

```
image::open <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src'
}
```

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

---

### `image::pixel`

```
image::pixel <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src',
    x:         null,
    y:         null
}
```

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

---

### `image::rgb2hex`

```
image::rgb2hex <R> {
    g:    <REQUIRED>,
    b:    <REQUIRED>,
    a:    null
}
```

Converts an RGB[A] color value to hexadecimal.

#### Arguments

- **r**, **g**, **b**, **a** (`int`):

    The 8-bit integer values (0-255) of the red, green, blue, (and optionally) alpha
    components of the color to convert.

#### Returns
A string representing the hexadecimal color in the format `#RRGGBB` or `#RRGGBBAA`.

---


