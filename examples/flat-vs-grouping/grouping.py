from dude import select


@select(selector="css=.title", group="css=.custom-group")
def result_title(element):
    return {"title": element.text_content()}


@select(selector="css=.description", group="css=.custom-group")
def result_description(element):
    return {"description": element.text_content()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'grouping.html').absolute()}"
    dude.run(urls=[html])
