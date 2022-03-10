# lxml Scraper

Option to use [lxml](https://lxml.de/) as parser instead of Playwright has been added in [Release 0.6.0](https://github.com/roniemartinez/dude/releases/tag/0.6.0).
lxml is an optional dependency and can only be installed via `pip` using the command below.

=== "Terminal"

    ```bash
    pip install pydude[lxml]
    ```

## Required changes to your code in order to use lxml

Instead of ElementHandle objects when using Playwright as parser, [Element, "smart" strings, etc.](https://lxml.de/xpathxslt.html#xpath-return-values) objects are passed to the decorated functions.


=== "Python"

    ```python
    from dude import select


    @select(xpath='.//a[contains(@class, "url")]/@href') # (1)
    def result_url(href):
        return {"url": href} # (2)
    
    
    # Option to get url using cssselect
    @select(css="a.url", priority=2)
    def result_url(element):
        return {"url_css": element.attrib["href"]} # (3)
    
    
    @select(css='.title')
    def result_title(element):
        return {"title": element.text} # (4)
    ```
    
    1. Attributes can be accessed using XPath `@href`.
    2. When using XPath `@href` (or `text`), "smart" strings are returned.
    3. Attributes can also be accessed from lxml elements using `element.attrib["href"]`.
    4. Text content can be accessed from lxml elements using `element.text`.


## Running Dude with lxml 

You can run lxml parser using the `--lxml` command-line argument or `parser="lxml"` parameter to `run()`.


=== "Terminal"

    ```commandline
    dude scrape --url "<url>" --lxml --output data.json path/to/file.py
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["https://dude.ron.sh/"], parser="lxml", output="data.json")
    ```

## Limitations

1. Setup handlers are not supported.
2. Navigate handlers are not supported.


## Examples

Examples are can be found at [examples/lxml_sync.py](https://github.com/roniemartinez/dude/tree/master/examples/lxml_sync.py) and [examples/lxml_async.py](https://github.com/roniemartinez/dude/tree/master/examples/lxml_async.py).
