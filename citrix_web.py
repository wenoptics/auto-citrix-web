import contextlib
import logging

from playwright.async_api import Page, async_playwright

from context import Context

logger = logging.getLogger(__name__)


def _javascript_create_notice(txt: str):
    return f"""
      const el = document.createElement("div");
      el.appendChild(document.createTextNode("{txt}"));
      el.style.padding = '2em';
      el.style.fontSize = '2em';
      el.style.margin = '1em';
      el.style.border = '1px white solid';
      el.style.color = 'white';
      el.style.backgroundColor = 'rgba(100,100,100,0.8)';
      el.style.textAlign = 'center';

      document.querySelector('#logonbelt-bottomshadow')
        .appendChild(el);
    """


@contextlib.asynccontextmanager
async def citrix_login(ctx: Context, username: str, password: str, headless=False):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()

        # Open new page
        page = await context.new_page()

        # Go to https://ctxstore.ansys.com/vpn/index.html
        await page.goto("https://ctxstore.ansys.com/vpn/index.html")
        logger.debug('Page loaded.')

        await page.fill('input[id="Enter user name"]', username)
        await page.fill('input[id="passwd"]', password)
        await page.check('input[id="eula_check"]')
        logger.debug('Applied user inputs.')

        # Login and wait for login success
        with ctx.console.status("[bold blue]Waiting for login success...", spinner='dots') as status:
            # Create a notice
            await page.evaluate(_javascript_create_notice('Waiting for login response...'))

            ctx.console.log('Waiting for login response...')
            ctx.console.log('\n\nYou may need to respond to the login SSO request...\n\n')
            await page.click('input[id="Log_On"]')
            logger.debug('Log on button clicked.')

            # Click text=Skip Check
            await page.click("text=Skip Check")
            ctx.console.log('Skip Check applied.')
        # assert page.url == "https://ctxstore.ansys.com/Citrix/storeWeb-ext/"

        yield page

        # ---------------------
        await context.close()
        await browser.close()


async def load_apps(ctx: Context, page: Page):
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

    ctx.console.log(f'Available apps ({len(app_map)}): {list(app_map.keys())}')
    return app_map
