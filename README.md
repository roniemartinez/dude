# dude uncomplicated data extraction

Dude is a very simple framework to write a web scraper using Python decorators.
The design, inspired by [Flask](https://github.com/pallets/flask), was to easily build a web scraper in just a few lines of code.
Dude has an easy to learn syntax.

## Minimal web scraper

The simplest web scraper will look like this:

```python
from dude import select


@select(selector="a")
def get_links(element):
    return {"url": element.get_attribute("href")}
```

The example above will get all the [hyperlink](https://en.wikipedia.org/wiki/Hyperlink#HTML) elements in a page and calls the handler function `get_links()` for each element.
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

## Features

- Simple Flask-inspired design - build a scraper with decorators.
- Uses Playwright's API - run your scraper in Chrome, Firefox and Webkit and leverage Playwright's powerful selector engine.
- Data grouping - group related scraping data.
- URL pattern matching - run functions on specific URLs.
- Priority - reorder functions based on priority.
- Setup function - enable setup steps (clicking dialogs or login).
- Navigate function - enable navigation steps to move to other pages.
- Custom storage - option to save data to other formats or database.
- Async support - write async handlers.

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

### Basic Usage

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

The included [examples/flat.py](examples/flat.py) code was written to scrape Google Search results ("q=dude"). You can run the example in your terminal using the command `python examples/flat.py`.

### Advanced Usage

#### Setup

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

#### Navigate

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

#### Grouping Results

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

A more extensive example can be found at [examples/grouping.py](examples/grouping.py).

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

##### The `group` parameter simplifies how you write your code

> ℹ️ The examples below are both acceptable way to write a scraper. You have the option to choose how you write the code.

A common way developers write scraper can be illustrated using this example below (see [examples/single_handler.py](examples/single_handler.py) for the complete script).
While this works, it can be hard to maintain.

```python
@select(selector="css=.g")
def result_handler(element):
    """
    Perform all the heavy-lifting in a single handler.
    """
    data = {}

    url = element.query_selector("*css=a >> css=h3:nth-child(2)")
    if url:
        data["url"] = url.get_attribute("href")

    title = element.query_selector("h3:nth-child(2)")
    if title:
        data["title"] = element.text_content()

    description = element.query_selector("css=div[style='-webkit-line-clamp\\3A 2']")
    if description:
        data["description"] = element.text_content()

    return data
```

This can be rewritten in a much simpler way like below (see [examples/grouping.py](examples/grouping.py) for the complete script).
It will require you to write 3 simple functions but is much easier to read as you don't have to deal with querying the child elements.

```python
@select(selector="*css=a >> css=h3:nth-child(2)", group="css=.g")
def result_url(element):
    return {"url": element.get_attribute("href")}


@select(selector="css=h3:nth-child(2)", group="css=.g")
def result_title(element):
    return {"title": element.text_content()}


@select(selector="css=div[style='-webkit-line-clamp\\3A 2']", group="css=.g")
def result_description(element):
    return {"description": element.text_content()}
```

#### URL Pattern Matching

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

#### Prioritization

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

#### Custom Storage

Dude current supports `json`, `yaml/yml` and `csv` formats (the `Scraper` class only support `json`). 
However, this can be extended to support a custom storage or override the existing formats using the `@save()` decorator.
The save function should accept 2 parameters, `data` (list of dictionary of scraped data) and optional `output` (can be filename or `None`).
Take note that the save function must return a boolean for success.

The example below prints the output to terminal using tabulate for illustration purposes only. 
You can use the `@save()` decorator in other ways like saving the scraped data to spreadsheets, database or send it to an API.

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

The custom storage can then be called using any of these methods:

1. From terminal
    ```bash
    dude scrape --url "<url>" path/to/file.py --format table
    ```
2. From python
    ```python
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["<url>"], pages=2, format="table")
    ```

A more extensive example can be found at [examples/custom_storage.py](examples/custom_storage.py).

#### Using the Scraper application class

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

#### Async Support

Handler functions can be converted to async. It is not possible to mix async and sync handlers since Playwright does not support this.
It is however, possible to have async and sync storage handlers at the same time since this is not connected to Playwright anymore.

```python
@select(selector="css=h3:nth-child(2)", url=r".*\.com")
async def result_title(element):
    """
    Result title.
    """
    return {"title": await element.text_content()}

@save("json")
async def save_json(data, output) -> bool:
    ...
    return True

@save("xml")
def save_json5(data, output) -> bool:
    # sync storage handler can be used on sync and async mode
    ...
    return True
```

A more extensive example can be found at [examples/async.py](examples/async.py).

## CLI

```bash
% dude scrape -h                                                                 
usage: dude scrape [-h] --url URL [--headed] [--browser {chromium,webkit,firefox}] [--pages PAGES] [--output OUTPUT] [--format FORMAT] [--proxy-server PROXY_SERVER] [--proxy-user PROXY_USER]
                   [--proxy-pass PROXY_PASS]
                   PATH [PATH ...]

Run the dude scraper.

options:
  -h, --help            show this help message and exit

required arguments:
  PATH                  Path to python file/s containing the handler functions.
  --url URL             Website URL to scrape. Accepts one or more url (e.g. "dude scrape --url <url1> --url <url2> ...")

optional arguments:
  --headed              Run headed browser.
  --browser {chromium,webkit,firefox}
                        Browser type to use.
  --pages PAGES         Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined.
  --output OUTPUT       Output file. If not provided, prints into the terminal.
  --format FORMAT       Output file format. If not provided, uses the extension of the output file or defaults to "json". Supports "json", "yaml/yml", and "csv" but can be extended using the @save()
                        decorator.
  --proxy-server PROXY_SERVER
                        Proxy server.
  --proxy-user PROXY_USER
                        Proxy username.
  --proxy-pass PROXY_PASS
                        Proxy password.
```

## Why name this project "dude"?

- [X] A [Recursive acronym](https://en.wikipedia.org/wiki/Recursive_acronym) looks nice.
- [X] Adding "uncomplicated" (like [`ufw`](https://wiki.ubuntu.com/UncomplicatedFirewall)) into the name says it is a very simple framework. 
- [X] Puns! I also think that if you want to do web scraping, there's probably some random dude around the corner who can make it very easy for you to start with it. 😊

## Author

[Ronie Martinez](mailto:ronmarti18@gmail.com)
