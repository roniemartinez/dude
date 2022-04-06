from dude import select


@select(css="a.url", url_match=lambda x: x.endswith(".html"))
@select(css="a.url", url_match="*dude.ron.sh/*")
def result_url(element):
    return {"url": element.get_attribute("href")}


@select(css=".title", url_match=lambda x: x.endswith(".html"))
@select(css=".title", url_match="*dude.ron.sh/*")
def result_title(element):
    return {"title": element.text_content()}


@select(css=".description", url_match=lambda x: x.endswith(".html"))
@select(css=".description", url_match="*dude.ron.sh/*")
def result_description(element):
    return {"description": element.text_content()}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html, "https://dude.ron.sh"])
