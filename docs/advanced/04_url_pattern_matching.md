# URL Pattern Matching

In order to make a handler function to run on specific websites, a `url` pattern parameter can be passed to `@select()` decorator.
The `url_match` parameter should be valid Unix shell-style wildcards (see https://docs.python.org/3/library/fnmatch.html) or custom function that returns a boolean. 
The example below will only run if the URL of the current page matches `*.com/*`.

=== "Python"

    ```python
    from dude import select
    
    
    @select(css=".title", url_match="*.com/*")
    def result_title(element):
        return {"title": element.text_content()}


    @select(css="a.url", url_match=lambda x: x.endswith(".html"))
    def result_url(element):
        return {"url": element.get_attribute("href")}
    ```

## Examples

A more extensive example can be found at [examples/url_pattern.py](https://github.com/roniemartinez/dude/tree/master/examples/url_pattern.py).
