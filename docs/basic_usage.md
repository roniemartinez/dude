# Basic Usage

To use `dude`, start by importing the library.

=== "Python"

    ```python
    from dude import select
    ```

A basic handler function consists of the structure below. 
A handler function should accept 1 argument (element) and should be decorated with `@select()`. 
The handler should return a dictionary.
Click on the annotations (+ sign) for more details.


=== "Python"

    ```python
    @select(selector="<put-your-selector-here>") # (1)
    def handler(element): # (2)
        ... # (3)
        return {"<key>": "<value-extracted-from-element>"} # (4)
    ```

    1. `@select()` decorator.
    2. Function should accept 1 parameter, the element object found in the page being scraped.
    3. You can specify your Python algorithm here.
    4. Return a dictionary. This can contain an arbitrary amount of key-value pairs.

The example handler below extracts the text content of any element that matches the selector `css=.title`.

=== "Python"

    ```python
    from dude import select
    
    
    @select(selector="css=.title")
    def result_title(element):
        """
        Result title.
        """
        return {"title": element.text_content()}
    ```

It is possible to attach a single handler to multiple selectors.

=== "Python"

    ```python
    from dude import select
    
    
    @select(selector="<a-selector>")
    @select(selector="<another-selector>")
    def handler(element):
        return {"<key>": "<value-extracted-from-element>"}
    ```

## How to run the scraper

To start scraping, use any of the following options. Click on the annotations (+ sign) for more details.

=== "Terminal"

    ```bash
    dude scrape --url "<url>" --output data.json path/to/file.py #(1)
    ```
    
    1. You can run your scraper from terminal/shell/command-line by supplying URLs, the output filename of your choice and the paths to your python codes to `dude scrape` command.

=== "Python"

    ```python
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["https://dude.ron.sh/"]) #(1)
    ```

    1. You can also use **dude.run()** function and run **python path/to/file.py** from terminal.

## Examples

Check out the example in [examples/flat.py](examples/flat.py) and run it on your terminal using the command `python examples/flat.py`.
