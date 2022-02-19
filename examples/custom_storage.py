import tabulate

from dude import save, select


@save("table")
def save_table(data, output) -> bool:
    """
    Prints data to stdout using tabulate.
    """
    print(tabulate.tabulate(tabular_data=data, headers="keys", maxcolwidths=50))
    return True


@select(selector="css=div#rso h3:nth-child(2)")
def result_title(element):
    """
    Result title.
    """
    return {"title": element.text_content()}


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

    dude.run(urls=["https://www.google.com/search?q=dude&hl=en"], pages=2, format="table")
