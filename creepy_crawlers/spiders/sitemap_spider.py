from scrapy import Request
from scrapy.spiders import SitemapSpider

class MySpider(SitemapSpider):
   name="myspidy"

   sitemap_urls = ["https://www.halfords.com/sitemap_index.xml"]
   sitemap_rules = []
   def _parse_sitemap(self, response):
        # yield a request for each url in the txt file that matches your filters
        print("respons eis ", response)
        urls = response.text.splitlines()
        it = self.sitemap_filter(urls)
        for loc in it:
            for r, c in self._cbs:
                if r.search(loc):
                    yield Request(loc, callback=c)
                    break