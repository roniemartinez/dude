# Prioritization

Handlers are sorted based on the following sequence:

1. URL Pattern
2. Group
3. Selector
4. Priority

If all handlers have the same priority value, they will be executed based on which handler was inserted first into the rule list.
This arrangement depends on how handlers are defined inside python files and which python files was imported first.
If no priority was provided to `@select()` decorator, the value defaults to 100.

The example below makes sure that `result_description()` will be called first before `result_title()`.


=== "Python"

    ```python
    from dude import select


    @select(selector="css=.title", priority=1)
    def result_title(element):
        return {"title": element.text_content()}
    
    
    @select(selector="css=.description", priority=0)
    def result_description(element):
        return {"description": element.text_content()}
    ```

The priority value is most useful on Setup and Navigate handlers. As an example below, the selector `css=#pnnext` will be queried first before looking for `text=Next`.
Take note that if `css=#pnnext` exists, then `text=Next` will not be queried anymore.

=== "Python"

    ```python
    from dude import select
    
    
    @select(selector="text=Next", navigate=True)
    @select(selector="css=#pnnext", navigate=True, priority=0)
    def next_page(element, page):
        with page.expect_navigation():
            element.click()
    ```

## Examples

A more extensive example can be found at [examples/priority.py](https://github.com/roniemartinez/dude/tree/master/examples/priority.py).
