<table>
    <tr>
        <td>License</td>
        <td><img src='https://img.shields.io/pypi/l/pydude.svg?style=for-the-badge' alt="License"></td>
        <td>Version</td>
        <td><img src='https://img.shields.io/pypi/v/pydude.svg?logo=pypi&style=for-the-badge' alt="Version"></td>
    </tr>
    <tr>
        <td>Github Actions</td>
        <td><img src='https://img.shields.io/github/workflow/status/roniemartinez/dude/Python?label=actions&logo=github%20actions&style=for-the-badge' alt="Github Actions"></td>
        <td>Coverage</td>
        <td><img src='https://img.shields.io/codecov/c/github/roniemartinez/dude/branch?label=codecov&logo=codecov&style=for-the-badge' alt="CodeCov"></td>
    </tr>
    <tr>
        <td>Supported versions</td>
        <td><img src='https://img.shields.io/pypi/pyversions/pydude.svg?logo=python&style=for-the-badge' alt="Python Versions"></td>
        <td>Wheel</td>
        <td><img src='https://img.shields.io/pypi/wheel/pydude.svg?style=for-the-badge' alt="Wheel"></td>
    </tr>
    <tr>
        <td>Status</td>
        <td><img src='https://img.shields.io/pypi/status/pydude.svg?style=for-the-badge' alt="Status"></td>
        <td>Downloads</td>
        <td><img src='https://img.shields.io/pypi/dm/pydude.svg?style=for-the-badge' alt="Downloads"></td>
    </tr>
</table>

# dude uncomplicated data extraction

Dude is a very simple framework for writing a web scraper using Python decorators.
The design, inspired by [Flask](https://github.com/pallets/flask), was to easily build a web scraper in just a few lines of code.
Dude has an easy-to-learn syntax.

> 🚨 Dude is currently in Pre-Alpha. Please expect breaking changes.

## Installation

To install, simply run the following from terminal.

```bash
pip install pydude
playwright install  # Install playwright binaries for Chrome, Firefox and Webkit.
```

## Minimal web scraper

The simplest web scraper will look like this:

```python
from dude import select


@select(css="a")
def get_link(element):
    return {"url": element.get_attribute("href")}
```

The example above will get all the [hyperlink](https://en.wikipedia.org/wiki/Hyperlink#HTML) elements in a page and calls the handler function `get_link()` for each element.

## How to run the scraper

You can run your scraper from terminal/shell/command-line by supplying URLs, the output filename of your choice and the paths to your python scripts to `dude scrape` command.

```bash
dude scrape --url "<url>" --output data.json path/to/script.py
```

## Features

- Simple [Flask](https://github.com/pallets/flask)-inspired design - build a scraper with decorators.
- Uses [Playwright](https://playwright.dev/python/) API - run your scraper in Chrome, Firefox and Webkit and leverage Playwright's powerful selector engine supporting CSS, XPath, text, regex, etc.
- Data grouping - group related scraping data.
- URL pattern matching - run functions on specific URLs.
- Priority - reorder functions based on priority.
- Setup function - enable setup steps (clicking dialogs or login).
- Navigate function - enable navigation steps to move to other pages.
- Custom storage - option to save data to other formats or database.
- Async support - write async handlers.
- Option to use other parsers aside from Playwright.
  - [BeautifulSoup4](https://roniemartinez.github.io/dude/advanced/09_beautifulsoup4.html) - `pip install pydude[bs4]`
  - [Parsel](https://roniemartinez.github.io/dude/advanced/10_parsel.html) - `pip install pydude[parsel]`
  - [lxml](https://roniemartinez.github.io/dude/advanced/11_lxml.html) - `pip install pydude[lxml]`
  - [Pyppeteer](https://roniemartinez.github.io/dude/advanced/12_pyppeteer.html) - `pip install pydude[pyppeteer]`
  - [Selenium](https://roniemartinez.github.io/dude/advanced/13_selenium.html) - `pip install pydude[selenium]`

## Supported Parsers

By default, Dude uses Playwright but gives you an option to use parsers that you are familiar with.
It is possible to use parser backends like 
[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), 
[Parsel](https://github.com/scrapy/parsel),
[lxml](https://lxml.de/),
[Pyppeteer](https://github.com/pyppeteer/pyppeteer), 
and [Selenium](https://github.com/SeleniumHQ/Selenium).

Here is the summary of features supported by each parser.

<table>
<thead>
  <tr>
    <td rowspan="2" style='text-align:center;'>Parser Backend</td>
    <td rowspan="2" style='text-align:center;'>Supports<br>Sync?</td>
    <td rowspan="2" style='text-align:center;'>Supports<br>Async?</td>
    <td colspan="4" style='text-align:center;'>Selectors</td>
    <td rowspan="2" style='text-align:center;'><a href="https://roniemartinez.github.io/dude/advanced/01_setup.html">Setup<br>Handler</a></td>
    <td rowspan="2" style='text-align:center;'><a href="https://roniemartinez.github.io/dude/advanced/02_navigate.html">Navigate<br>Handler</a></td>
  </tr>
  <tr>
    <td>CSS</td>
    <td>XPath</td>
    <td>Text</td>
    <td>Regex</td>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Playwright</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>BeautifulSoup4</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>Parsel</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>lxml</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>Pyppeteer</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Selenium</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
</tbody>
</table>

## Documentation

Read the complete documentation at [https://roniemartinez.github.io/dude/](https://roniemartinez.github.io/dude/).
All the advanced and useful features are documented there.

## Support

This project is at a very early stage. This dude needs some love! ❤️

Contribute to this project by feature requests, idea discussions, reporting bugs, opening pull requests, or through Github Sponsors. Your help is highly appreciated.

[![Github Sponsors](https://img.shields.io/github/sponsors/roniemartinez?label=github%20sponsors&logo=github%20sponsors&style=for-the-badge)](https://github.com/sponsors/roniemartinez)

## Requirements

- ✅ Any dude should know how to work with selectors (CSS or XPath).
- ✅ This library was built on top of [Playwright](https://github.com/microsoft/playwright-python). Any dude should be at least familiar with the basics of Playwright - they also extended the selectors to support text, regular expressions, etc. See [Selectors | Playwright Python](https://playwright.dev/python/docs/selectors).
- ✅ Python decorators... you'll live, dude!

## Why name this project "dude"?

- ✅ A [Recursive acronym](https://en.wikipedia.org/wiki/Recursive_acronym) looks nice.
- ✅ Adding "uncomplicated" (like [`ufw`](https://wiki.ubuntu.com/UncomplicatedFirewall)) into the name says it is a very simple framework. 
- ✅ Puns! I also think that if you want to do web scraping, there's probably some random dude around the corner who can make it very easy for you to start with it. 😊

## Author

[Ronie Martinez](mailto:ronmarti18@gmail.com)
