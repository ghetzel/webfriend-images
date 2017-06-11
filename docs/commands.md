# Command Reference

This module contains documentation on all of the commands supported by the WebFriend core
distribution.  Additional commands may be included via plugins.

## Documentation

All commands are documented by describing the format for executing the command.  All supported
options are presented, along with their default values.  If an option is required, it will be
shown with the value `<REQUIRED>`.

- [Image](#image-command-set)
   - [image::extract_text](#imageextract_text)
   - [image::info](#imageinfo)
   - [image::open](#imageopen)
   - [image::pixel](#imagepixel)
   - **[image::rgb2hex](#imagergb2hex)**

## `image` Command Set

### `image::extract_text`

```
image::extract_text <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src',
    language:  'eng'
}
```

---

### `image::info`

```
image::info <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src'
}
```

---

### `image::open`

```
image::open <SELECTOR> {
    url:       null,
    file:      null,
    attribute: 'src'
}
```

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

- **r**, **g**, **b*, **a** (`int`):

    The 8-bit integer values (0-255) of the red, green, blue, (and optionally) alpha
    components of the color to convert.

#### Returns
A string representing the hexadecimal color in the format `#RRGGBB` or `#RRGGBBAA`.

---


