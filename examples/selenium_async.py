from dude import select


@select(css="a.url")
async def result_url(element):
    return {"url": element.get_attribute("href")}


@select(css=".title")
async def result_title(element):
    return {"url": element.text}


@select(css=".description")
async def result_description(element):
    return {"url": element.text}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html], parser="selenium")
