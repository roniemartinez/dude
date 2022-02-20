import tabulate

from dude import save, select


@save("table")
def save_table(data, output) -> bool:
    """
    Prints data to stdout using tabulate.
    """
    print(tabulate.tabulate(tabular_data=data, headers="keys", maxcolwidths=50))
    return True


@select(selector="css=a.url")
def result_url(element):
    return {"url": element.get_attribute("href")}


if __name__ == "__main__":
    from pathlib import Path

    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html], format="table")
