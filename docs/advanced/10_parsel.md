# Parsel Scraper

Option to use [Parsel](https://github.com/scrapy/parsel) as parser backend instead of Playwright has been added in [Release 0.5.0](https://github.com/roniemartinez/dude/releases/tag/0.5.0).
Parsel is an optional dependency and can only be installed via `pip` using the command below.

=== "Terminal"

    ```bash
    pip install pydude[parsel]
    ```

## Required changes to your script in order to use Parsel

Instead of ElementHandle objects when using Playwright as parser backend, Selector objects are passed to the decorated functions.


=== "Python"

    ```python
    from dude import select
    
    
    @select(css="a.url::attr(href)") # (1)
    def result_url(selector):
        return {"url": selector.get()} # (2)
    
    
    @select(css=".title::text") # (3)
    def result_title(selector):
        return {"title": selector.get()}
    ```
    
    1. Attributes can be accessed by CSS non-standard pseudo-element, `::attr(name)`.
    2. Values from Selector objects can be accessed using `.get()` method.
    3. Texts can be accessed by CSS non-standard pseudo-element, `::text`.


## Running Dude with Parsel 

You can run Parsel parser backend using the `--parsel` command-line argument or `parser="parsel"` parameter to `run()`.


=== "Terminal"

    ```commandline
    dude scrape --url "<url>" --parsel --output data.json path/to/script.py
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["https://dude.ron.sh/"], parser="parsel", output="data.json")
    ```

## Limitations

1. Setup handlers are not supported.
2. Navigate handlers are not supported.


## Examples

Examples are can be found at [examples/parsel_sync.py](https://github.com/roniemartinez/dude/tree/master/examples/parsel_sync.py) and [examples/parsel_async.py](https://github.com/roniemartinez/dude/tree/master/examples/parsel_async.py).
