# @start_requests decorator

The `@start_requests` decorator adds an option to send custom HTTP methods (POST, PUT, PATCH, etc).

!!! warning

    `@start_requests()` is only supported on BeautifulSoup4, lxml and Parsel backends.

To register custom Request objects, simply wrap a generator with `@start_requests` decorator.
Click on the annotations (+ sign) for more details.

=== "Python"

    ```python
    from dude import Request # (1)


    @start_requests()
    def custom_requests():
        for url in ["https://dude.ron.sh"]:
            yield Request(method="GET", url=url) # (2)
    
    
    @select(css="a.url")
    def result_url(soup):
        return {"url": soup["href"]}
    
    
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=[], parser="bs4") # (3)
    ```

    1. Import the `Request` class.
    2. It is necessary to specify the HTTP method.
    3. `url` param should be set to an empty list if not needed.