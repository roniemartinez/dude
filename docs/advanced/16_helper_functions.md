# Helper Functions

Here is a list of functions that can be useful for web scraping.

## `follow_url()`

This function allows adding dynamically created URLs to the list of URLs to be scraped.

=== "Python"

    ```python
    from dude import select, follow_url


    @select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:

        follow_url(element["href"])

        return {"url": element["href"]}
    ```

## `get_current_url()`

This functions allows access to the current URL that is being scraped.
It can be useful when used together with `follow_url()` function.

=== "Python"

    ```python
    from dude import select, follow_url, get_current_url


    @select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:

        follow_url(urljoin(get_current_url(), element["href"]))

        return {"url": element["href"]}
    ```
