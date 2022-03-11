# Pyppeteer Scraper

Option to use [Pyppeteer](https://github.com/pyppeteer/pyppeteer) as parser instead of Playwright has been added in [Release 0.8.0](https://github.com/roniemartinez/dude/releases/tag/0.8.0).
Pyppeteer is an optional dependency and can only be installed via `pip` using the command below.

=== "Terminal"

    ```bash
    pip install pydude[pyppeteer]
    pyppeteer-install # (1)
    ```

    1. Download recent version of Chromium

## Required changes to your script in order to use Pyppeteer

Instead of Playwright's `ElementHandle` objects when using Playwright as parser, Pyppeteer has its own `ElementHandle` objects that are passed to the decorated functions.
The decorated functions will need to accept 2 arguments, `element` and `page` objects. 
This is needed because Pyppeteer elements does not expose a convenient function to get the text content.

!!! info

    Pyppeteer only supports async

=== "Python"

    ```python
    from dude import select


    @select(css="a.url")
    async def result_url(element, page): # (1)
        handle = await element.getProperty("href") # (2)
        return {"url": await handle.jsonValue()} # (3)
    
    
    @select(css=".title")
    async def result_title(element, page):
        return {"title": await page.evaluate("(element) => element.textContent", element)} # (4)
    ```

    1. In addition to `element` objects, `page` objects are also needed.
    2. Attributes/Properties can be accessed using `getProperty()`.
    3. `jsonValue()` is used to convert Pyppeteer objects to Python types.
    4. `Page.evaluate()` is used to get the element's text content.

## Running Dude with Pyppeteer 

You can run Pyppeteer parser using the `--pyppeteer` command-line argument or `parser="pyppeteer"` parameter to `run()`.

=== "Terminal"

    ```commandline
    dude scrape --url "<url>" --pyppeteer --output data.json path/to/script.py
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["https://dude.ron.sh/"], parser="pyppeteer", output="data.json")
    ```

## Limitations

1. Pyppeteer only supports async.
2. Pyppeteer does not support XPath 2.0, therefore not allowing regular expression.

## Examples

Examples are can be found at [examples/pyppeteer_async.py](https://github.com/roniemartinez/dude/tree/master/examples/pyppeteer_async.py).
