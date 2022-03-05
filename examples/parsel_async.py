from dude import select

"""
This example demonstrates how to use Parsel + async HTTPX

To access an attribute, use:
    selector.attrib["href"]
To get the text, use ::text pseudo-selector, then:
    selector.get()
"""


@select(css="a.url", priority=2)
async def result_url(selector):
    return {"url": selector.attrib["href"]}


@select(css=".title::text", priority=1)
async def result_title(selector):
    return {"title": selector.get()}


@select(css=".description::text", priority=0)
async def result_description(selector):
    return {"description": selector.get()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html, "https://dude.ron.sh"], parser="parsel")
