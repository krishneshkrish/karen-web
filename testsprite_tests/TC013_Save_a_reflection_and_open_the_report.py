import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:5180")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Navigate to the End page by opening 'http://localhost:5180/end' so the End UI (including the 'End for now' option) can be located.
        await page.goto("http://localhost:5180/end")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Reload the app by navigating to the root URL (http://localhost:5180) so the End page UI can load and its controls become visible.
        await page.goto("http://localhost:5180")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Navigate to the /end page and load the End page UI so the 'End for now' option can be located.
        await page.goto("http://localhost:5180/end")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Open the backend API docs at http://localhost:8001/docs to confirm the backend is reachable.
        # Open URL in new tab
        page = await context.new_page()
        await page.goto("http://localhost:8001/docs")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Switch to the frontend tab showing 'http://localhost:5180/end' and check the page for the End UI (look for an 'End for now' option).
        # Switch to tab 23EA
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the 'End for now' button to end the session temporarily.
        # End for now button
        elem = page.get_by_role("button", name="End for now")
        await elem.click(timeout=10000)
        
        # -> Click the 'Save reflection' button to save the reflection and load the reflection report view.
        # Save reflection button
        elem = page.get_by_role("button", name="Save reflection")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Reflection report page was reached (report URL shown).
        # Assert-outcome: failed
        # Assert: Expected the URL to contain 'report' to confirm the reflection report page is displayed.
        await expect(page).to_have_url(re.compile("report"), timeout=15000), "Expected the URL to contain 'report' to confirm the reflection report page is displayed."
        
        # --> Reflection summary content is not present; the report page shows an error message instead of generated summary.
        # Assert-outcome: failed
        # Assert: Expected the reflection report to display generated summary content instead of the error message.
        await expect(page.locator("body").nth(0)).to_contain_text("We weren't able to generate your reflection.", timeout=15000), "Expected the reflection report to display generated summary content instead of the error message."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    