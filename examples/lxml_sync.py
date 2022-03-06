from dude import select

"""
This example demonstrates how to use lxml + HTTPX

To access an attribute, use:
    element.attrib["href"]
You can also access an attribute using the xpath @href, for example ".//a[contains(@class, "url")]/@href",
which returns a string.
"""


@select(xpath='.//a[contains(@class, "url")]/@href', priority=2)
def result_url(href):
    return {"url": href}


# Option to get url using cssselect
@select(css="a.url", priority=2)
def result_url_css(element):
    return {"url_css": element.attrib["href"]}


@select(xpath='.//p[contains(@class, "title")]/text()', priority=1)
def result_title(text):
    return {"title": text}


@select(xpath='.//p[contains(@class, "description")]/text()', priority=0)
def result_description(text):
    return {"description": text}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html, "https://dude.ron.sh"], parser="lxml")
