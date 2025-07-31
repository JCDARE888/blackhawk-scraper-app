import csv
import asyncio
from playwright.async_api import async_playwright

async def run_scraper(url_list, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Title", "Price (JPY)", "SKU", "Product URL"])

            for category_url in url_list:
                page_num = 1
                while True:
                    paged_url = f"{category_url}?page={page_num}"
                    await page.goto(paged_url, timeout=60000)
                    await asyncio.sleep(2)

                    product_cards = await page.query_selector_all(".product-grid-item")
                    if not product_cards:
                        break

                    for card in product_cards:
                        title_el = await card.query_selector(".product-name")
                        price_el = await card.query_selector(".product-price")
                        link_el = await card.query_selector("a")

                        title = await title_el.inner_text() if title_el else "N/A"
                        price = await price_el.inner_text() if price_el else "N/A"
                        href = await link_el.get_attribute("href") if link_el else None
                        product_url = f"https://www.blackhawkjapan.com{href}" if href else "N/A"

                        sku = "N/A"
                        if product_url != "N/A":
                            try:
                                await page.goto(product_url)
                                await asyncio.sleep(1.5)
                                rows = await page.query_selector_all("table tr")
                                for row in rows:
                                    cells = await row.query_selector_all("td")
                                    if len(cells) >= 2:
                                        label = await cells[0].inner_text()
                                        if "Product Code" in label:
                                            sku = await cells[1].inner_text()
                                            break
                            except:
                                pass

                        writer.writerow([title, price, sku, product_url])

                    page_num += 1

        await browser.close()
