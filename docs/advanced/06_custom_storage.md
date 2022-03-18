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

## Examples

A more extensive example can be found at [examples/custom_storage.py](https://github.com/roniemartinez/dude/tree/master/examples/custom_storage.py).
