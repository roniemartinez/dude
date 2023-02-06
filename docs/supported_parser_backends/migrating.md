# Migrating Your Web Scrapers to Dude

Here are examples showing how web scrapers are commonly written compared to how they will be when written in Dude.

## Playwright

Example: Scrape Google search results

=== "Using pure Playwright"

    ```python
    import itertools
    import json
    
    from playwright.sync_api import sync_playwright
    
    
    def main(urls, output, headless, pages):
        results = []
    
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
    
            for url in urls:
                page.goto(url)
    
                # click I agree
                with page.expect_navigation():
                    page.locator('text="I agree"').click()
    
                for page_number in range(1, pages + 1):
                    for group in page.query_selector_all(".g"):
                        url_elements = group.query_selector_all("*css=a >> h3:nth-child(2)")
                        title_elements = group.query_selector_all("h3:nth-child(2)")
                        description_elements = group.query_selector_all("div[style='-webkit-line-clamp\\3A 2']")
    
                        # group together since each .g div can contain more than one set of results
                        for url_element, title_element, description_element in itertools.zip_longest(
                            url_elements, title_elements, description_elements
                        ):
                            results.append(
                                {
                                    "url": url_element.get_attribute("href") if url_element else None,
                                    "title": title_element.text_content() if title_element else None,
                                    "description": description_element.text_content() if description_element else None,
                                    "page": page_number,
                                }
                            )
    
                    # go to next page
                    with page.expect_navigation():
                        page.locator("text=Next").click()

            browser.close()
    
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
    
    
    if __name__ == "__main__":
        main(urls=["https://www.google.com/search?q=dude&hl=en"], output="data.json", headless=False, pages=2)

    ```

=== "Using Playwright with Dude"
    
    ```python
    from dude import select
    
    
    @select(selector="*css=a >> h3:nth-child(2)", group_css=".g")
    def result_url(element):
        return {"url": element.get_attribute("href")}
    
    
    @select(css="h3:nth-child(2)", group_css=".g")
    def result_title(element):
        return {"title": element.text_content()}
    
    
    @select(css="div[style='-webkit-line-clamp\\3A 2']", group_css=".g")
    def result_description(element):
        return {"description": element.text_content()}
    
    
    @select(text="I agree", setup=True)
    def agree(element, page):
        with page.expect_navigation():
            element.click()
    
    
    @select(text="Next", navigate=True)
    def next_page(element, page):
        with page.expect_navigation():
            element.click()
    
    
    if __name__ == "__main__":
        import dude
    
        dude.run(
            urls=["https://www.google.com/search?q=dude&hl=en"],
            output="data.json",
            headless=False,
            pages=2,
        )

    ```

## BeautifulSoup4

Example: Get all links, titles and descriptions from [https://dude.ron.sh](https://dude.ron.sh)

=== "Using HTTPX + BeautifulSoup4"

    ```python
    import itertools
    import json
    
    import httpx
    from bs4 import BeautifulSoup
    
    
    def main(urls, output):
        results = []
    
        with httpx.Client() as client:
            for url in urls:
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    content = response.text
                except httpx.HTTPStatusError as e:
                    raise
    
                soup = BeautifulSoup(content, "html.parser")

                for group in soup.select(".custom-group"):
                    url_elements = group.select("a.url")
                    title_elements = group.select(".title")
                    description_elements = group.select(".description")
    
                    # group together since each .custom-group div can contain more than one set of results
                    for url_element, title_element, description_element in itertools.zip_longest(
                        url_elements, title_elements, description_elements
                    ):
                        results.append(
                            {
                                "url": url_element["href"] if url_element else None,
                                "title": title_element.get_text() if title_element else None,
                                "description": description_element.get_text() if description_element else None,
                            }
                        )
    
            with open(output, "w") as f:
                json.dump(results, f, indent=2)
    
    
    if __name__ == "__main__":
        main(urls=["https://dude.ron.sh"], output="data.json")

    ```

=== "Using BeautifulSoup4 with Dude"
    
    ```python
    from dude import select
    
    
    @select(css="a.url", group_css=".custom-group")
    def result_url(soup):
        return {"url": soup["href"]}
    
    
    @select(css=".title", group_css=".custom-group")
    def result_title(soup):
        return {"title": soup.get_text()}
    
    
    @select(css=".description", group_css=".custom-group")
    def result_description(soup):
        return {"description": soup.get_text()}
    
    
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["https://dude.ron.sh"], parser="bs4", output="data.json")

    ```

## Parsel

Example: Get all links, titles and descriptions from [https://dude.ron.sh](https://dude.ron.sh)

=== "Using HTTPX + Parsel"

    ```python
    import itertools
    import json
    
    import httpx
    from parsel import Selector
    
    
    def main(urls, output):
        results = []
    
        with httpx.Client() as client:
            for url in urls:
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    content = response.text
                except httpx.HTTPStatusError as e:
                    raise
    
                selector = Selector(content)
                for group in selector.css(".custom-group"):
                    hrefs = group.css("a.url::attr(href)")
                    titles = group.css(".title::text")
                    descriptions = group.css(".description::text")
    
                    # group together since each .custom-group div can contain more than one set of results
                    for href, title, description in itertools.zip_longest(hrefs, titles, descriptions):
                        results.append(
                            {
                                "url": href.get() if href else None,
                                "title": title.get() if title else None,
                                "description": description.get() if description else None,
                            }
                        )
    
            with open(output, "w") as f:
                json.dump(results, f, indent=2)
    
    
    if __name__ == "__main__":
        main(urls=["https://dude.ron.sh"], output="data.json")

    ```

=== "Using Parsel with Dude"
    
    ```python
    from dude import select
    
    
    @select(css="a.url::attr(href)", group_css=".custom-group")
    def result_url(selector):
        return {"url": selector.get()}
    
    
    @select(css=".title::text", group_css=".custom-group")
    def result_title(selector):
        return {"title": selector.get()}
    
    
    @select(css=".description::text", group_css=".custom-group")
    def result_description(selector):
        return {"description": selector.get()}
    
    
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["https://dude.ron.sh"], parser="parsel", output="data.json")

    ```

## lxml

Example: Get all links, titles and descriptions from [https://dude.ron.sh](https://dude.ron.sh)

=== "Using HTTPX + lxml + cssselect"

    ```python
    import itertools
    import json
    
    import httpx
    from lxml import etree
    
    
    def main(urls, output):
        results = []
    
        with httpx.Client() as client:
            for url in urls:
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    content = response.text
                except httpx.HTTPStatusError as e:
                    raise
    
                tree = etree.HTML(text=content)
                for group in tree.cssselect(".custom-group"):
                    hrefs = group.xpath('.//a[contains(@class, "url")]/@href')
                    titles = group.xpath('.//p[contains(@class, "title")]/text()')
                    descriptions = group.xpath('.//p[contains(@class, "description")]/text()')
    
                    # group together since each .custom-group div can contain more than one set of results
                    for href, title, description in itertools.zip_longest(hrefs, titles, descriptions):
                        results.append(
                            {
                                "url": href,
                                "title": title,
                                "description": description,
                            }
                        )
    
            with open(output, "w") as f:
                json.dump(results, f, indent=2)
    
    
    if __name__ == "__main__":
        main(urls=["https://dude.ron.sh"], output="data.json")

    ```

=== "Using lxml with Dude"
    
    ```python
    from dude import select
    
    
    @select(xpath='.//a[contains(@class, "url")]/@href', group_css=".custom-group")
    def result_url(href):
        return {"url": href}
    
    
    @select(xpath='.//p[contains(@class, "title")]/text()', group_css=".custom-group")
    def result_title(text):
        return {"title": text}
    
    
    @select(xpath='.//p[contains(@class, "description")]/text()', group_css=".custom-group")
    def result_description(text):
        return {"description": text}
    
    
    if __name__ == "__main__":
        import dude
    
        dude.run(urls=["https://dude.ron.sh"], parser="lxml", output="data.json")

    ```
