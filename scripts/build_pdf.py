from pathlib import Path
from playwright.sync_api import sync_playwright
import re

html = Path("index.html").read_text(encoding="utf-8")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    for theme in ("light", "dark"):
        context = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        page = context.new_page()
        source = re.sub(r'data-print-theme="(?:light|dark)"', 'data-print-theme="'+theme+'"', html, count=1)
        page.set_content(source, wait_until="domcontentloaded")
        page.emulate_media(media="print")
        page.evaluate("document.fonts.ready")
        output = "cv5-"+theme+".pdf"
        page.pdf(path=output, prefer_css_page_size=True,
                 print_background=True, display_header_footer=False)
        context.close()
    browser.close()

import fitz
for filename in ("cv5-light.pdf", "cv5-dark.pdf"):
    pdf=fitz.open(filename)
    assert len(pdf)==2, f"{filename} generated {len(pdf)} pages, expected 2"
    assert all(abs(p.rect.width-612)<1 and abs(p.rect.height-792)<1 for p in pdf), f"{filename}: not US Letter"
    assert all("THINK BOT" in p.get_text() and "SPEAK HUMAN" in p.get_text() for p in pdf), f"{filename}: missing footer"
    assert "Earlier Operations, Sales" in pdf[1].get_text(), f"{filename}: wrong page-two start"
    print(f"{filename}: verified 2 US Letter pages with both footers")
