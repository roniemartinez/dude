from dude import select


@select(selector="css=a.url", group="css=.custom-group")
def result_url(element):
    return {"url": element.get_attribute("href")}


@select(selector="css=.title", group="css=.custom-group")
def result_title(element):
    return {"title": element.text_content()}


@select(selector="css=.description", group="css=.custom-group")
def result_description(element):
    return {"description": element.text_content()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html])
