"""Export technical-document.html to PDF: `python3 docs/diagrams/html/export_pdf.py`.

Needs Playwright with Chromium (`pip install playwright && playwright install chromium`).
Run build.py first so the HTML is current.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "technical-document.html"
OUT = HERE / "technical-document.pdf"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(SRC.as_uri(), wait_until="networkidle")  # wait for the web fonts
        page.emulate_media(media="print")
        page.pdf(path=str(OUT), format="A4", print_background=True, prefer_css_page_size=True,
                 display_header_footer=True, header_template="<span></span>",
                 footer_template='<div style="font:8px monospace;color:#6A6253;width:100%;text-align:center">'
                                 'Cohesiq technical design document · <span class="pageNumber"></span> / '
                                 '<span class="totalPages"></span></div>')
        browser.close()
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
