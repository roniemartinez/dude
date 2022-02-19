from dude import select


@select(selector="css=div#rso >> *css=a >> css=h3:nth-child(2)")
async def result_url(element):
    """
    Result URL.

    We only want the selector for the hyperlink (*css=a).
    See https://playwright.dev/python/docs/selectors#intermediate-matches.
    """
    return {"url": await element.get_attribute("href")}


@select(selector="css=div#rso h3:nth-child(2)")
async def result_title(element):
    """
    Result title.
    """
    return {"title": await element.text_content()}


@select(selector="css=div[style='-webkit-line-clamp\\3A 2']")
async def result_description(element):
    """
    Result description.
    """
    return {"description": await element.text_content()}


@select(selector="text=I agree", setup=True)
async def agree(element, page):
    """
    Clicks "I agree" in order to use the website.
    """
    async with page.expect_navigation():
        await element.click()


@select(selector="text=Next", navigate=True)
async def next_page(element, page):
    """
    Clicks the Next button/link to navigate to the next page.
    """
    async with page.expect_navigation():
        await element.click()


if __name__ == "__main__":
    import dude

    dude.run(urls=["https://www.google.com/search?q=dude&hl=en"], pages=2)
