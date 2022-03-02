# Grouping Results

When scraping a page containing a list of information, for example, containing URLs, titles and descriptions, it is important to know how data can be grouped together. 
By default, all scraped results are grouped by `:root` which is the root document.
To specify grouping, pass `group=<selector-for-grouping>` to `@select()` decorator.

In the example below, the results are grouped by an element with class `custom-group`. The matched selectors should be children of this element.
Click on the annotations (+ sign) for more details.

=== "Python"
    
    ```python
    from dude import select
    
    
    @select(selector="css=.title", group="css=.custom-group") # (1)
    def result_title(element):
        return {"title": element.text_content()}
    ```

    1. Group the results by the CSS selector `.custom-group`.

A more extensive example can be found at [examples/grouping.py](https://github.com/roniemartinez/dude/tree/master/examples/grouping.py).

## Why we need to group the results

The `group` parameter has the advantage of making sure that items are in their correct group. 
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

When the group is not specified, the default grouping will be used it will result in "**Description 3**" being grouped with "**Title 2**".

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

By specifying the group in `@select(..., group="css=.custom-group")`, we will be able to get a better result.

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

## The `group` parameter simplifies how you write your code

!!! info

    The examples below are both acceptable way to write a scraper. You have the option to choose how you write your code.

A common way developers write scraper can be illustrated using this example below (see [examples/single_handler.py](https://github.com/roniemartinez/dude/tree/master/examples/single_handler.py) for the complete script).

While this works, it can be hard to maintain.

=== "Performing all actions in one function"

    ```python
    from dude import select


    @select(selector="css=.custom-group")
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

This can be rewritten in a much simpler way like below (see [examples/grouping.py](https://github.com/roniemartinez/dude/tree/master/examples/grouping.py) for the complete script).

It will only require us to write 3 simple functions but is much easier to read as we don't have to deal with querying the child elements, ourselves.

=== "Separate handlers with grouping"

    ```python
    from dude import select


    @select(selector="css=a.url", group="css=.custom-group")
    def result_url(element):
        return {"url": element.get_attribute("href")}
    
    
    @select(selector="css=.title", group="css=.custom-group")
    def result_title(element):
        return {"title": element.text_content()}
    
    
    @select(selector="css=.description", group="css=.custom-group")
    def result_description(element):
        return {"description": element.text_content()}
    ```
