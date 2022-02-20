from dude import select


@select(selector="css=.g")
def result_handler(element):
    """
    Perform all the heavy-lifting in a single handler.
    """
    data = {}

    # We only want the selector for the hyperlink (*css=a)
    # See https://playwright.dev/python/docs/selectors#intermediate-matches.
    url = element.query_selector("*css=a >> css=h3:nth-child(2)")
    if url:
        data["url"] = url.get_attribute("href")

    title = element.query_selector("h3:nth-child(2)")
    if title:
        data["title"] = element.text_content()

    description = element.query_selector("css=div[style='-webkit-line-clamp\\3A 2']")
    if description:
        data["description"] = element.text_content()

    return data


@select(selector="text=I agree", setup=True)
def agree(element, page):
    """
    Clicks "I agree" in order to use the website.
    """
    with page.expect_navigation():
        element.click()


@select(selector="text=Next", navigate=True)
def next_page(element, page):
    """
    Clicks the Next button/link to navigate to the next page.
    """
    with page.expect_navigation():
        element.click()


if __name__ == "__main__":
    import dude

    dude.run(urls=["https://www.google.com/search?q=dude&hl=en"], pages=2)
