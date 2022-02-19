from dude import Scraper

app = Scraper()


@app.select(selector="css=div#rso >> *css=a >> css=h3:nth-child(2)")
def result_url(element):
    """
    Result URL.

    We only want the selector for the hyperlink (*css=a).
    See https://playwright.dev/python/docs/selectors#intermediate-matches.
    """
    return {"url": element.get_attribute("href")}


@app.select(selector="css=div#rso h3:nth-child(2)")
def result_title(element):
    """
    Result title.
    """
    return {"title": element.text_content()}


@app.select(selector="css=div[style='-webkit-line-clamp\\3A 2']")
def result_description(element):
    """
    Result description.
    """
    return {"description": element.text_content()}


@app.select(selector="text=I agree", setup=True)
def agree(element, page):
    """
    Clicks "I agree" in order to use the website.
    """
    with page.expect_navigation():
        element.click()


@app.select(selector="text=Next", navigate=True)
def next_page(element, page):
    """
    Clicks the Next button/link to navigate to the next page.
    """
    with page.expect_navigation():
        element.click()


if __name__ == "__main__":
    app.run(urls=["https://www.google.com/search?q=dude&hl=en"])
