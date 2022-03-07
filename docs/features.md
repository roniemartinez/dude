# Features

- Simple [Flask](https://github.com/pallets/flask)-inspired design - build a scraper with decorators.
- Uses [Playwright](https://playwright.dev/python/) API - run your scraper in Chrome, Firefox and Webkit and leverage Playwright's powerful selector engine supporting CSS, XPath, text, regex, etc.
- Data grouping - group related scraping data.
- URL pattern matching - run functions on specific URLs.
- Priority - reorder functions based on priority.
- Setup function - enable setup steps (clicking dialogs or login).
- Navigate function - enable navigation steps to move to other pages.
- Custom storage - option to save data to other formats or database.
- Async support - write async handlers.
- Option to use other parsers aside from Playwright.
    - [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - `pip install pydude[bs4]`
    - [Parsel](https://github.com/scrapy/parsel) - `pip install pydude[parsel]`
    - [lxml](https://lxml.de/) - `pip install pydude[lxml]`
    - [Pyppeteer](https://github.com/pyppeteer/pyppeteer) - `pip install pydude[pyppeteer]`
