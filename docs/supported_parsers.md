# Supported Parsers

By default, Dude uses Playwright but gives you an option to use parsers that you are familiar with.
It is possible to use parser backends like [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Parsel](https://github.com/scrapy/parsel) and [lxml](https://lxml.de/).

Here is the summary of features supported by each parser.

<table>
<thead>
  <tr>
    <td rowspan="2" style='text-align:center;'>Parser Backend</td>
    <td rowspan="2" style='text-align:center;'>Supports<br>Sync?</td>
    <td rowspan="2" style='text-align:center;'>Supports<br>Async?</td>
    <td colspan="4" style='text-align:center;'>Selectors</td>
    <td rowspan="2" style='text-align:center;'><a href="https://roniemartinez.github.io/dude/advanced/01_setup.html">Setup<br>Handler</a></td>
    <td rowspan="2" style='text-align:center;'><a href="https://roniemartinez.github.io/dude/advanced/02_navigate.html">Navigate<br>Handler</a></td>
  </tr>
  <tr>
    <td>CSS</td>
    <td>XPath</td>
    <td>Text</td>
    <td>Regex</td>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Playwright</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>BeautifulSoup4</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>Parsel</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>lxml</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>🚫</td>
  </tr>
  <tr>
    <td>Pyppeteer</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Selenium</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
    <td>🚫</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
</tbody>
</table>
