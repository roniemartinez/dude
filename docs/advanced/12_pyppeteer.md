# Pyppeteer Scraper

Option to use [Pyppeteer](https://github.com/pyppeteer/pyppeteer) as parser instead of Playwright has been added in [Release 0.8.0](https://github.com/roniemartinez/dude/releases/tag/0.8.0).
Pyppeteer is an optional dependency and can only be installed via `pip` using the command below.

=== "Terminal"

    ```bash
    pip install pydude[pyppeteer]
    pyppeteer-install # (1)
    ```

    1. Download recent version of Chromium

## Required changes to your code in order to use Pyppeteer

Instead of Playwright's ElementHandle objects when using Playwright as parser, Pyppeteer has its own ElementHandle objects that are passed to the decorated functions.


=== "Python"

    ```python
    from dude import select


    ```


## Running Dude with Pyppeteer 

You can run Pyppeteer parser using the `--pyppeteer` command-line argument or `parser="pyppeteer"` parameter to `run()`.


=== "Terminal"

    ```commandline
    dude scrape --url "<url>" --pyppeteer --output data.json path/to/file.py
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["https://dude.ron.sh/"], parser="pyppeteer", output="data.json")
    ```


## Examples

Examples are can be found at [examples/pyppeteer_sync.py](https://github.com/roniemartinez/dude/tree/master/examples/pyppeteer_sync.py) and [examples/pyppeteer_async.py](https://github.com/roniemartinez/dude/tree/master/examples/pyppeteer_async.py).
