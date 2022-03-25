# Custom Storage

Dude currently support `json`, `yaml/yml` and `csv` formats only (the [`Scraper`](07_the_scraper_application_class.html) class only support `json`). 
However, this can be extended to support a custom storage or override the existing formats using the `@save()` decorator.
The save function should accept 2 parameters, `data` (list of dictionary of scraped data) and optional `output` (can be filename or `None`).
Take note that the save function must return a boolean for success.

The example below prints the output to terminal using tabulate for illustration purposes only. 
You can use the `@save()` decorator in other ways like saving the scraped data to spreadsheets, database or send it to an API.

=== "Python"

    ```python
    from dude import save
    import tabulate


    @save("table")
    def save_table(data, output) -> bool:
        """
        Prints data to stdout using tabulate.
        """
        print(tabulate.tabulate(tabular_data=data, headers="keys", maxcolwidths=50))
        return True
    ```

The custom storage above can then be called using any of the options below.


=== "Terminal"

    ```bash
    dude scrape --url "<url>" path/to/script.py --format table
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["<url>"], pages=2, format="table")
    ```

## Saving on every page

It is possible to call the save functions after each page.
This is useful when running in spider mode to prevent lost of data.
To make use of this option, the flag `is_per_page` in the `@save()` should be set to `True`.

=== "Python"

    ```python
    @save("table", is_per_page=True)
    def save_table(data, output) -> bool:
        ...
    ```

To run the scraper in per-page save, pass `--save-per-page` argument.

=== "Terminal"

    ```bash
    dude scrape --url "<url>" path/to/script.py --format table --save-per-page
    ```

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude

        dude.run(urls=["<url>"], pages=2, format="table", save_per_page=True)
    ```

!!! note

    The option `--save-per-page` is best used with events to make sure that connections or file handles are opened 
    and closed properly. Check the examples below.

## Examples

A more extensive example can be found at [examples/custom_storage.py](https://github.com/roniemartinez/dude/tree/master/examples/custom_storage.py) and
[examples/save_per_page.py](https://github.com/roniemartinez/dude/tree/master/examples/save_per_page.py).
