# Command-Line Interface (CLI)

=== "CLI"

    ```commandline
    usage: dude scrape [-h] --url URL [--playwright | --bs4] [--headed] [--browser {chromium,webkit,firefox}] [--pages PAGES] [--output OUTPUT] [--format FORMAT] [--proxy-server PROXY_SERVER]
                       [--proxy-user PROXY_USER] [--proxy-pass PROXY_PASS]
                       PATH [PATH ...]
    
    Run the dude scraper.
    
    options:
      -h, --help            show this help message and exit
    
    required arguments:
      PATH                  Path to python file/s containing the handler functions.
      --url URL             Website URL to scrape. Accepts one or more url (e.g. "dude scrape --url <url1> --url <url2> ...")
    
    optional arguments:
      --playwright          Use Playwright.
      --bs4                 Use BeautifulSoup4.
      --headed              Run headed browser.
      --browser {chromium,webkit,firefox}
                            Browser type to use.
      --pages PAGES         Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined.
      --output OUTPUT       Output file. If not provided, prints into the terminal.
      --format FORMAT       Output file format. If not provided, uses the extension of the output file or defaults to "json". Supports "json", "yaml/yml", and "csv" but can be extended using the @save()
                            decorator.
      --proxy-server PROXY_SERVER
                            Proxy server.
      --proxy-user PROXY_USER
                            Proxy username.
      --proxy-pass PROXY_PASS
                            Proxy password.
    ```
