import asyncio

from playwright.async_api import Playwright, async_playwright
import config


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Open new page
    page = await context.new_page()

    # Go to https://ctxstore.ansys.com/vpn/index.html
    await page.goto("https://ctxstore.ansys.com/vpn/index.html")

    await page.fill('input[id="Enter user name"]', config.settings.USERNAME)
    await page.fill('input[id="passwd"]', config.settings.PASSWORD)
    await page.check('input[id="eula_check"]')

    await page.evaluate("""
      // create a new element
      const newSpan = document.createElement("span");
      newSpan.appendChild(document.createTextNode("Waiting for logging response..."));
      newSpan.classList.add('plain')
      newSpan.classList.add('form_text')
      newSpan.style.padding = '2em';
      newSpan.style.fontSize = '2em';
    
      document.querySelector('form[name="vpnForm"]')
        .appendChild(newSpan);
    """)
    await page.click('input[id="Log_On"]')

    # Click text=Skip Check
    await page.click("text=Skip Check")
    # assert page.url == "https://ctxstore.ansys.com/Citrix/storeWeb-ext/"

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
