import shutil
import uuid
from pathlib import Path

from dude import post_setup, pre_setup, shutdown, startup

SAVE_DIR: Path


@startup()
def initialize_csv():
    """
    Connection to databases or API and other use-cases can be done here before the web scraping process is started.
    """
    global SAVE_DIR
    SAVE_DIR = Path(__file__).resolve().parent / "temp"
    SAVE_DIR.mkdir(exist_ok=True)


@pre_setup()
def screenshot(page):
    """
    Perform actions here after loading a page (or after a successful HTTP response) and before modifying things in the
    setup stage.
    """
    unique_name = str(uuid.uuid4())
    page.screenshot(path=SAVE_DIR / f"{unique_name}.png")  # noqa


@post_setup()
def print_pdf(page):
    """
    Perform actions here after running the setup stage.
    """
    unique_name = str(uuid.uuid4())
    page.pdf(path=SAVE_DIR / f"{unique_name}.pdf")  # noqa


@shutdown()
def zip_all():
    """
    Perform actions here before the application is terminated.
    """
    global SAVE_DIR
    shutil.make_archive("images-and-pdfs", "zip", SAVE_DIR)


if __name__ == "__main__":
    import dude

    html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
    dude.run(urls=[html])
