# Selenium Scraper

Option to use [Selenium](https://github.com/SeleniumHQ/Selenium) as parser instead of Playwright has been added in [Release 0.9.0](https://github.com/roniemartinez/dude/releases/tag/0.9.0).
Selenium is an optional dependency and can only be installed via `pip` using the command below.

=== "Terminal"

    ```bash
    pip install pydude[selenium]
    ```

## Required changes to your code in order to use Selenium

Instead of Playwright's `ElementHandle` objects when using Playwright as parser, `WebElement` objects are passed to the decorated functions.

!!! info

    Selenium only supports sync

=== "Python"

    ```python
    from dude import select


    @select(css="a.url")
    def result_url(element, page):
        return {"url": element.get_attribute("href")}
    
    
    @select(css=".title")
    def result_title(element, page):
        return {"title": element.text}
    ```

## Running Dude with Selenium 

You can run Selenium parser using the `--selenium` command-line argument or `parser="selenium"` parameter to `run()`.

=== "Terminal"

    ```commandline
    dude scrape --url "<url>" --selenium --output data.json path/to/file.py
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["https://dude.ron.sh/"], parser="selenium", output="data.json")
    ```

## Limitations

1Selenium does not support XPath 2.0, therefore not allowing regular expression.

## Examples

Examples are can be found at [examples/selenium_sync.py](https://github.com/roniemartinez/dude/tree/master/examples/selenium_sync.py) and [examples/selenium_async.py](https://github.com/roniemartinez/dude/tree/master/examples/selenium_async.py).