# dude uncomplicated data extraction

Dude, this is a simple way to write a web scraper using Python decorators.

## Why name this project "dude"?

I wanted to add "uncomplicated" (like `ufw`) into the name together with something related to web scraping.

I also think that if you want to do web scraping, there's probably some random dude who can make it very easy for you to start with. 😊

## Support

If you like `dude` or if it is useful to you, show your support by sponsoring my projects.

[![Github Sponsors](https://img.shields.io/github/sponsors/roniemartinez?label=github%20sponsors&logo=github%20sponsors&style=for-the-badge)](https://github.com/sponsors/roniemartinez)

## How to use

### Requirements

1. Any dude should know how to work with selectors (CSS or XPath).
2. This library was built on top of [Playwright](https://github.com/microsoft/playwright-python). Any dude should be at least familiar with the basics of Playwright - they also extended the selectors to support text, regular expressions, etc. See [Selectors | Playwright Python](https://playwright.dev/python/docs/selectors).
3. Python decorators... you'll live, dude!

### Installation

### Example

The included [example.py](example.py) code was written to scrape Google Search results ("dude"). You can run the example in your terminal using the command `python example.py`.

#### Basics

To use `dude`, start by importing the library.

```python
from dude import select
```

A basic handler function consists of the structure below. A handler function should accept 1 argument (element) and should be decorated with `@select()`. The handler should return a dictionary.

```python
@select(selector="<put-your-selector-here>")
def handler(element):
    ...
    # This dictionary can contain multiple items
    return {"<key>": "<value-extracted-from-element>"}

```

The example handler below extracts the text content of any element that matches the selector `css=div#rso h3:nth-child(2)`.

```python
@select(selector="css=div#rso h3:nth-child(2)")
def result_title(element):
    """
    Result title.
    """
    return {"title": element.text_content()}
```

To run your handler functions, simply call `dude.run(url=<url-you-want-to-scrape>)`.

```python
import dude

dude.run(url="https://www.google.com/search?q=dude&hl=en")
```

#### Advanced

##### Setup

Some websites might require you to click on dialog buttons. You can pass `setup=True` parameter to declare the setup actions.

```python
@select(selector="text=I agree", setup=True)
def agree(element, page):
    """
    Clicks "I agree" in order to use the website.
    """
    with page.expect_navigation():
        element.click()
```

##### Navigate

To navigate to another page, you can pass `navigate=True` parameter to declare the navigate actions.

```python
@select(selector="text=Next", navigate=True)
def next_page(element, page):
    """
    Clicks the Next button/link to navigate to the next page.
    """
    with page.expect_navigation():
        element.click()
```

## Author

[Ronie Martinez](mailto:ronmarti18@gmail.com)
