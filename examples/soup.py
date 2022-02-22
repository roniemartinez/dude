from dude import select

"""
This example demonstrates how to use BeautifulSoup4.

To access an attribute, use:
    soup["href"]
To get the text, use:
    soup.get_text()
"""


@select(selector="a.url", priority=2)
def result_url(soup):
    return {"url": soup["href"]}


@select(selector=".title", priority=1)
def result_title(soup):
    return {"title": soup.get_text()}


@select(selector=".description", priority=0)
def result_description(soup):
    return {"description": soup.get_text()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html], use_bs4=True)
