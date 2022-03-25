import json
from pathlib import Path
from typing import IO

from dude import save, select, shutdown, startup

jsonl_file: IO


@select(css="a.url")
def result_url(element):
    return {"url": element.get_attribute("href")}


@startup()
def initialize_jsonl():
    global jsonl_file
    jsonl_file = open("output.jsonl", "w")


@shutdown()
def close_jsonl():
    global jsonl_file
    jsonl_file.close()


@save("jsonl", is_per_page=True)
def save_jsonl(data, output) -> bool:
    global jsonl_file
    jsonl_file.writelines((json.dumps(item) + "\n" for item in data))
    return True


if __name__ == "__main__":
    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html], format="jsonl", save_per_page=True)
