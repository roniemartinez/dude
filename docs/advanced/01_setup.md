# Setup

Setup handlers are very useful when performing initial actions after loading a website for the first time. 
Setup handlers could perform any of the following:

1. Login
2. Click on dialogs buttons

To create a Setup handler, you can pass `setup=True` parameter to `@select()` decorator. 
The only difference with Setup and normal element handler is that setup functions should accept 2 parameters, the element matched by the selector and the Page object (or WebDriver object in Selenium).
Click on the annotations (+ sign) for more details.

=== "Python"

    ```python
    from dude import select
    
    
    @select(text="I agree", setup=True) # (1)
    def agree(element, page):
        """
        Clicks "I agree" in order to use the website.
        """
        with page.expect_navigation(): # (2)
            element.click() # (3)
    ```

    1. Finds an element containing the text "I agree".
    2. (Playwright) We expect that after clicking the element, it will navigate us to our page of interest.
    3. (Playwright) Perform click on the element.

!!! info

    You can have multiple Setup steps, make sure to set the **[priority](05_prioritization.html)** to run them in order.
