from dude import select


@select(selector="css=a.url")
async def result_url(element):
    return {"url": await element.get_attribute("href")}


@select(selector="css=.title")
async def result_title(element):
    return {"title": await element.text_content()}


@select(selector="css=.description")
async def result_description(element):
    return {"description": await element.text_content()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html])
