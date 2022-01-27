import asyncio
import contextlib
import shutil
from pathlib import Path

from rich import print
from playwright.async_api import Playwright, async_playwright, Page
import config

assert config.settings.get('auth', 'USERNAME')
assert config.settings.get('auth', 'PASSWORD')


@contextlib.asynccontextmanager
async def citrix_login(playwright: Playwright, username: str, password: str):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Open new page
    page = await context.new_page()

    # Go to https://ctxstore.ansys.com/vpn/index.html
    await page.goto("https://ctxstore.ansys.com/vpn/index.html")

    await page.fill('input[id="Enter user name"]', username)
    await page.fill('input[id="passwd"]', password)
    await page.check('input[id="eula_check"]')

    # Create a notice
    await page.evaluate("""
      const el = document.createElement("div");
      el.appendChild(document.createTextNode("Waiting for login response..."));
      el.style.padding = '2em';
      el.style.fontSize = '2em';
      el.style.margin = '1em';
      el.style.border = '1px white solid';
      el.style.color = 'white';
      el.style.backgroundColor = 'rgba(100,100,100,0.8)';
      el.style.textAlign = 'center';

      document.querySelector('#logonbelt-bottomshadow')
        .appendChild(el);
    """)
    await page.click('input[id="Log_On"]')

    # Click text=Skip Check
    await page.click("text=Skip Check")
    # assert page.url == "https://ctxstore.ansys.com/Citrix/storeWeb-ext/"

    yield page

    # ---------------------
    await context.close()
    await browser.close()


async def start_citrix_app(playwright: Playwright, app_start='Remote Desktop Manager') -> None:
    async with citrix_login(
            playwright,
            config.settings.get('auth', 'USERNAME'),
            config.settings.get('auth', 'PASSWORD')
    ) as page:
        page: Page

        # Wait for the app list
        el_app_list = page.locator("ul.storeapp-list")
        await el_app_list.wait_for()

        el_app_items = el_app_list.locator("li")
        app_map = {}
        for idx in range(await el_app_items.count()):
            ele = el_app_items.nth(idx)
            app_name = await ele.locator('.storeapp-name').text_content()
            # app_image = await ele.locator('img.storeapp-icon').get_attribute('src')
            app_map[app_name] = el_app_items.nth(idx)

        print('Available apps', list(app_map.keys()))
        if app_start not in app_map:
            raise ValueError(f'Not found app named "{app_start}"')

        async with page.expect_download() as download_info:
            await app_map[app_start].locator('.storeapp-details-link').click()
        download = await download_info.value
        # waits for download to complete
        path = await download.path()
        print(f'Downloaded to "{path}" (from "{download.url}")')

        dst = Path(r'C:\Users\wenop\OneDrive\Desktop')
        shutil.copy(path, dst / 'start.ica')


async def main() -> None:
    async with async_playwright() as playwright:
        await start_citrix_app(playwright)


asyncio.run(main())
