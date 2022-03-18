# Grouping Results

When scraping a page containing a list of information, for example, containing URLs, titles and descriptions, it is important to know how data can be grouped together. 
By default, all scraped results are grouped by `:root` which is the root document.
To specify grouping, pass `group=<selector-for-grouping>` to `@select()` decorator.

In the example below, the results are grouped by an element with class `custom-group`. The matched selectors should be children of this element.
Click on the annotations (+ sign) for more details.

=== "Python"
    
    ```python
    from dude import select
    
    
    @select(css=".title", group=".custom-group") # (1)
    def result_title(element):
        return {"title": element.text_content()}
    ```

    1. Group the results by the CSS selector `.custom-group`.


You can also specify groups by using the `@group()` decorator and passing the argument `selector="<selector-for-grouping>"`.

=== "Python"
    
    ```python
    from dude import group, select
    
    
    @group(css=".custom-group") # (1)
    @select(css=".title")
    def result_title(element):
        return {"title": element.text_content()}
    ```

    1. Group the results by the CSS selector `.custom-group`.

## Supported group selector types

The `@select()` decorator does not only accept `group` but also `group_css`, `group_xpath`, `group_text` and `group_regex`.
Please take note that `group_css`, `group_xpath`, `group_text` and `group_regex` are specific and `group` can contain any of these types.

=== "Python"

    ```python
    from dude import select
    
    
    @select(css=".title", group_css="<css-selector>")     # (1)
    @select(css=".title", group_xpath="<xpath-selector>") # (2)
    @select(css=".title", group_text="<text-selector>")   # (3)
    @select(css=".title", group_regex="<regex-selector>") # (4)
    def handler(element):
        return {"<key>": "<value-extracted-from-element>"}
    ```

    1. Group CSS Selector
    2. Group XPath Selector
    3. Group Text Selector
    4. Group Regular Expression Selector

It is possible to use 2 or more of these types at the same time but only one will be used taking the precedence `group` -> `css` -> `xpath` -> `text` -> `regex`.

Like the `@select()` decorator, the `@group()` decorator also accepts `selector`, `css`, `xpath`, `text` and `regex`.
Similarly, `css`, `xpath`, `text` and `regex` are specific and `selector` can contain any of these types.

=== "Python"

    ```python
    from dude import select
    
    
    @group(css="<css-selector>") # (1)
    @select(selector="<selector>") 
    def handler(element):
        return {"<key>": "<value-extracted-from-element>"}
    ```

    1. CSS Selector

It is possible to use 2 or more of these types at the same time but only one will be used taking the precedence `selector` -> `css` -> `xpath` -> `text` -> `regex`.

## Why we need to group the results

The `group` parameter or the `@group()` decorator has the advantage of making sure that items are in their correct group. 
Take for example the HTML source below, notice that in the second `div`, there is no description.

=== "HTML"

    ```html
        <div class="custom-group">
            <p class="title">Title 1</p>
            <p class="description">Description 1</p>
        </div>
        <div class="custom-group">
            <p class="title">Title 2</p>
        </div>
        <div class="custom-group">
            <p class="title">Title 3</p>
            <p class="description">Description 3</p>
        </div>
    ```

When the group is not specified, the default grouping will be used which will result in "**Description 3**" being grouped with "**Title 2**".

=== "Default Grouping"

    ```json5
    [
      {
        "_page_number": 1,
        // ...
        "description": "Description 1",
        "title": "Title 1"
      },
      {
        "_page_number": 1,
        // ...
        "description": "Description 3",
        "title": "Title 2"
      },
      {
        "_page_number": 1,
        // ...
        "title": "Title 3"
      }
    ]
    ```

By specifying the group in `@select(..., group=".custom-group")`, we will be able to get a better result.

=== "Specified Grouping"

    ```json5
    [
      {
        "_page_number": 1,
        // ...
        "description": "Description 1",
        "title": "Title 1"
      },
      {
        "_page_number": 1,
        // ...
        "title": "Title 2"
      },
      {
        "_page_number": 1,
        // ...
        "description": "Description 3",
        "title": "Title 3"
      }
    ]
    ```

## Groups simplify how you write your script

!!! info

    The examples below are both acceptable way to write a scraper. You have the option to choose how you write your script.

A common way developers write scraper can be illustrated using this example below (see [examples/single_handler.py](https://github.com/roniemartinez/dude/tree/master/examples/single_handler.py) for the complete script).

While this works, it can be hard to maintain.

=== "Performing all actions in one function"

    ```python
    from dude import select


    @select(css=".custom-group")
    def result_handler(element):
        """
        Perform all the heavy-lifting in a single handler.
        """
        data = {}
    
        url = element.query_selector("a.url")
        if url:
            data["url"] = url.get_attribute("href")
    
        title = element.query_selector(".title")
        if title:
            data["title"] = title.text_content()
    
        description = element.query_selector(".description")
        if description:
            data["description"] = description.text_content()
    
        return data
    ```

It will only require us to write 3 simple functions but is much easier to read as we don't have to deal with querying the child elements, ourselves.

=== "Separate handlers with grouping"

    ```python
    from dude import group, select


    @select(css="a.url", group=".custom-group")
    def result_url(element):
        return {"url": element.get_attribute("href")}
    
    
    @select(css=".title", group=".custom-group")
    def result_title(element):
        return {"title": element.text_content()}
    
    
    @select(css=".description", group=".custom-group")
    def result_description(element):
        return {"description": element.text_content()}
    ```

## When are `@group()` decorator and `group` parameter used by Dude

1. If the `group` parameter is present, it will be used for grouping.
2. If the `group` parameter is not present, the selector in the `@group()` decorator will be used for grouping.
3. If both `group` parameter and `@group()` decorator are not present, the `:root` element will be used for grouping.

!!! info

    Use `@group()` decorator when using multiple `@select()` decorators in one function in order to reduce repetition.
    

## Examples

- Grouping by `@group()` decorator: [examples/group_decorator.py](https://github.com/roniemartinez/dude/tree/master/examples/group_decorator.py).
- Grouping by passing `group` parameter to `@select()` decorator: [examples/group_in_select.py](https://github.com/roniemartinez/dude/tree/master/examples/group_in_select.py).