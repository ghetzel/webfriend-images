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
    url:       null,
    file:      null,
    attribute: 'src',
    language:  'eng'
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


