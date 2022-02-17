# dude uncomplicated data extraction

Dude is a very simple framework to write a web scraper using Python decorators.
The design, inspired by [Flask](https://github.com/pallets/flask), was to easily build a web scraper in just a few lines of code.

## Minimal web scraper

The simplest web scraper will look like this:

```python
from dude import select


@select(selector="a")
def get_links(element):
    return {"url": element.get_attribute("href")}
```

To start scraping, just simply run in your terminal:

```bash
dude scrape --url "<url>" path/to/file.py
```

Another option is to run from python code by calling `dude.run()` like below and running `python path/to/file.py`:

```python
from dude import select


@select(selector="a")
def get_links(element):
    return {"url": element.get_attribute("href")}


if __name__ == "__main__":
    import dude

    dude.run(url="https://www.google.com/search?q=dude&hl=en")
```

## Why name this project "dude"?

- [X] A [Recursive acronym](https://en.wikipedia.org/wiki/Recursive_acronym).
- [X] Add "uncomplicated" (like [`ufw`](https://wiki.ubuntu.com/UncomplicatedFirewall)) into the name.
- [X] Puns! I also think that if you want to do web scraping, there's probably some random dude around the corner who can make it very easy for you to start with it. 😊

## Support

This project is at a very early stage. This dude needs some love! ❤️

Contribute to this project by feature requests, idea discussions, reporting bugs, opening pull requests, or through Github Sponsors. Your help is highly appreciated.

[![Github Sponsors](https://img.shields.io/github/sponsors/roniemartinez?label=github%20sponsors&logo=github%20sponsors&style=for-the-badge)](https://github.com/sponsors/roniemartinez)

## How to use

### Requirements

- [X] Any dude should know how to work with selectors (CSS or XPath).
- [X] This library was built on top of [Playwright](https://github.com/microsoft/playwright-python). Any dude should be at least familiar with the basics of Playwright - they also extended the selectors to support text, regular expressions, etc. See [Selectors | Playwright Python](https://playwright.dev/python/docs/selectors).
- [X] Python decorators... you'll live, dude!

### Installation

### Example

The included [examples/flat.py](examples/flat.py) code was written to scrape Google Search results ("q=dude"). You can run the example in your terminal using the command `python example.py`.

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

##### Grouping results

When scraping a page containing a list of information, for example, a Search Engine Results Page (SERP) can have URLs, titles and descriptions,
it is important to know how data can be grouped. By default, all scraped results are grouped by `:root` which is the root document, creating a flat list.
To specify grouping, pass `group=<selector-for-grouping>` to `@select()` decorator.

In the example below, the results are grouped by an element with class `g`. The matched selectors should be children of this element.

```python
@select(selector="css=h3:nth-child(2)", group="css=.g")
def result_title(element):
    """
    Result title.
    """
    return {"title": element.text_content()}
```

A more extensive example can be found at [examples/grouped.py](examples/grouped.py).

##### URL Pattern Matching

In order to use a handler function to just specific websites, a `url` pattern parameter can be passed to `@select()`.
The `url` pattern parameter should be a valid regular expression. 
The example below will only run if the URL of the current page matches `.*\.com`.

```python
@select(selector="css=h3:nth-child(2)", url=r".*\.com")
def result_title(element):
    """
    Result title.
    """
    return {"title": element.text_content()}
```

A more extensive example can be found at [examples/url_pattern.py](examples/url_pattern.py).

##### Using the Application object

The decorator `@select()` and the function `run()` simplifies the usage of the framework.
It is possible to create your own application object using the example below.

> 🚨 WARNING: This is not currently supported by the command line interface! 
Please use the command `python path/to/file.py` when running the application.

```python

from dude import Application


app = Application()

@app.select(selector="css=h3:nth-child(2)", url=r".*\.com")
def result_title(element):
    return {"title": element.text_content()}


if __name__ == '__main__':
    app.run(url="https://www.google.com/search?q=dude&hl=en")
```

A more extensive example can be found at [examples/application.py](examples/application.py).

## Author

[Ronie Martinez](mailto:ronmarti18@gmail.com)
