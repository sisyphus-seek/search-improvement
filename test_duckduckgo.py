#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/Search-Engines-Scraper')

from search_engines import Duckduckgo

# Try Duckduckgo instead
engine = Duckduckgo()
results = engine.search("nowledge mem wiki")
links = results.links()

print("DuckDuckGo - Found {} results:".format(len(links)))
for i, link in enumerate(links[:10], 1):
    print(f"{i}. {link}")
