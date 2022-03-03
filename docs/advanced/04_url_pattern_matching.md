# URL Pattern Matching

In order to make a handler function to run on specific websites, a `url` pattern parameter can be passed to `@select()` decorator.
The `url` pattern parameter should be a valid regular expression. 
The example below will only run if the URL of the current page matches `.*\.com`.

=== "Python"

    ```python
    from dude import select
    
    
    @select(selector=".title", url=r".*\.com")
    def result_title(element):
        return {"title": element.text_content()}
    ```

## Examples

A more extensive example can be found at [examples/url_pattern.py](https://github.com/roniemartinez/dude/tree/master/examples/url_pattern.py).
