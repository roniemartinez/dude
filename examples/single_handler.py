from dude import select


@select(css=".custom-group")
def result_handler(element):
    """
    Perform all the heavy-lifting in a single handler.
    """
    data = {}

    url = element.query_selector("a.url")
    if url:
        data["url"] = url.get_attribute("href")

    title = element.query_selector(".title")
    if title:
        data["title"] = title.text_content()

    description = element.query_selector(".description")
    if description:
        data["description"] = description.text_content()

    return data


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html])
