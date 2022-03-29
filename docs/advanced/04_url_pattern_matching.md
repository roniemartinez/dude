# URL Pattern Matching

In order to make a handler function to run on specific websites, a `url` pattern parameter can be passed to `@select()` decorator.
The `url` pattern parameter should be a valid Unix shell-style wildcards (see https://docs.python.org/3/library/fnmatch.html). 
The example below will only run if the URL of the current page matches `*.com/*`.

=== "Python"

    ```python
    from dude import select
    
    
    @select(css=".title", url="*.com/*")
    def result_title(element):
        return {"title": element.text_content()}
    ```

## Examples

A more extensive example can be found at [examples/url_pattern.py](https://github.com/roniemartinez/dude/tree/master/examples/url_pattern.py).
