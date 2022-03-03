from dude import group, select


@group(css=".custom-group")
@select(selector="a.url")
def result_url(element):
    return {"url": element.get_attribute("href")}


@group(css=".custom-group")
@select(selector=".title")
def result_title(element):
    return {"title": element.text_content()}


@group(css=".custom-group")
@select(selector=".description")
def result_description(element):
    return {"description": element.text_content()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html])
