# The **Scraper** Application Class

The decorators `@select()` and `@save()` and the function `run()` simplifies the usage of the framework.
It is possible to create your own scraper application object using the example below.

!!! warning

    🚨 This is not currently supported by the command-line interface!

    Please use the command `python path/to/file.py` to run the scraper application.

=== "Python"

    ```python
    
    from dude import Scraper
    
    
    app = Scraper()
    
    
    @app.select(selector=".title")
    def result_title(element):
        return {"title": element.text_content()}
    
    
    if __name__ == '__main__':
        app.run(urls=["https://dude.ron.sh/"])
    ```

## Examples

A more extensive example can be found at [examples/application.py](https://github.com/roniemartinez/dude/tree/master/examples/application.py).
