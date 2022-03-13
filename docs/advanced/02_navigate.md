# Navigate

Navigate handlers are used to move from page to page.

To create a Navigate handler, you can pass `navigate=True` parameter to `@select()` decorator. 
Like Setup handlers, Navigate handlers should accept 2 parameters, the element matched by the selector and the Page object (or WebDriver object in Selenium).
Click on the annotations (+ sign) for more details.

=== "Python"

    ```python
    from dude import select
    
    
    @select(text="Next", navigate=True) # (1)
    def next_page(element, page):
        """
        Clicks the Next button/link to navigate to the next page.
        """
        with page.expect_navigation(): # (2)
            element.click() # (3)
    ```

    1. Finds an element containing the text "Next".
    2. (Playwright) We expect that after clicking the element, it will navigate us to the next page.
    3. (Playwright) Perform click on the element.

!!! info

    You can have multiple Navigate steps, make sure to set the **[priority](05_prioritization.html)** to run them in order.
    When having multiple Navigate steps, only the first element found will be considered and all the succeeding selectors will be skipped.
