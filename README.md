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

    dude.run(urls=["https://www.google.com/search?q=dude&hl=en"])
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

To install, simply run:

```bash
pip install pydude
playwright install
```

The second command will install playwright binaries for Chrome, Firefox and Webkit. See https://playwright.dev/python/docs/intro#pip

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

To run your handler functions, simply call `dude.run(urls=["<url-you-want-to-scrape>"])`.

```python
import dude

dude.run(urls=["https://www.google.com/search?q=dude&hl=en"])
```

It is possible to attach a single handler to multiple selectors.

```python
@select(selector="<a-selector>")
@select(selector="<another-selector>")
def handler(element):
    return {"<key>": "<value-extracted-from-element>"}
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

The `group` parameter has the advantage of making sure that items are in their correct group. 
Take for example the HTML below, notice that in the second `div`, there is no description.

```html
    <div class="custom-group">
        <p class="title">Title 1</p>
        <p class="description">Description 1</p>
    </div>
    <div class="custom-group">
        <p class="title">Title 2</p>
    </div>
    <div class="custom-group">
        <p class="title">Title 3</p>
        <p class="description">Description 3</p>
    </div>
```

When the group is not specified, it will result in "Description 3" being grouped with "Title 2".

```json5
[
  {
    "page_number": 1,
    // ...
    "description": "Description 1",
    "title": "Title 1"
  },
  {
    "page_number": 1,
    // ...
    "description": "Description 3",
    "title": "Title 2"
  },
  {
    "page_number": 1,
    // ...
    "title": "Title 3"
  }
]
```

By specifying the group in `@select(..., group="css=.custom-group")`, we will be able to get a better result.

```json5
[
  {
    "page_number": 1,
    // ...
    "group_index": 0,
    "element_index": 0,
    "description": "Description 1",
    "title": "Title 1"
  },
  {
    "page_number": 1,
    // ...
    "group_index": 1,
    "element_index": 0,
    "title": "Title 2"
  },
  {
    "page_number": 1,
    // ...
    "group_index": 2,
    "element_index": 0,
    "description": "Description 3",
    "title": "Title 3"
  }
]
```

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

##### Prioritization

Handlers are sorted based on the following sequence:

1. URL Pattern
2. Group
3. Selector
4. Priority

If all handlers have the same priority value, they will be executed based on which handler was inserted into the rule list first.
This arrangement depends on how handlers are defined inside python files and which python files was imported first.
If no priority was provided to `@select()` decorator, the value defaults to 100.

The example below makes sure that `result_description()` will be called first before `result_title()`.

```python
@select(selector="css=div#rso h3:nth-child(2)", priority=1)
def result_title(element):
    return {"title": element.text_content()}


@select(selector="css=div[style='-webkit-line-clamp\\3A 2']", priority=0)
def result_description(element):
    return {"description": element.text_content()}
```

The priority value is most useful on Setup and Navigate handlers. As an example below, the selector `css=#pnnext` will be queried first before looking for `text=Next`.
Take note that if `css=#pnnext` exists, then `text=Next` will not be queried anymore.

```python
@select(selector="text=Next", navigate=True)
@select(selector="css=#pnnext", navigate=True, priority=0)
def next_page(element, page):
    with page.expect_navigation():
        element.click()
```

A more extensive example can be found at [examples/priority.py](examples/priority.py).

##### Custom Storage

Dude current supports `json`, `yaml/yml` and `csv` formats (the Scraper object only support `json`). 
However, this can be extended to support custom storage or override the existing formats using the `@save()` decorator.
The save function should accept 2 parameters, `data` (list of dictionary of scraped data) and optional `output` (can be filename or `None`).
Take note that the save function must return a boolean for success.

```python
import tabulate


@save("table")
def save_table(data, output) -> bool:
    """
    Prints data to stdout using tabulate.
    """
    print(tabulate.tabulate(tabular_data=data, headers="keys", maxcolwidths=50))
    return True
```

This will be called using any of these methods.

###### From terminal

```bash
dude scrape --url "<url>" path/to/file.py --format table
```

###### From python

```python
if __name__ == "__main__":
    import dude

    dude.run(urls=["<url>"], pages=2, format="table")
```

A more extensive example can be found at [examples/custom_storage.py](examples/custom_storage.py).

##### Using the Scraper application object

The decorator `@select()` and the function `run()` simplifies the usage of the framework.
It is possible to create your own scraper application object using the example below.

> 🚨 WARNING: This is not currently supported by the command line interface! 
Please use the command `python path/to/file.py` to run the scraper application.

```python

from dude import Scraper

app = Scraper()


@app.select(selector="css=h3:nth-child(2)", url=r".*\.com")
def result_title(element):
    return {"title": element.text_content()}


if __name__ == '__main__':
    app.run(urls=["https://www.google.com/search?q=dude&hl=en"])
```

A more extensive example can be found at [examples/application.py](examples/application.py).

## Author

[Ronie Martinez](mailto:ronmarti18@gmail.com)
