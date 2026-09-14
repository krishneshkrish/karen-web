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
        
        # -> Open the '/end' page by navigating to http://localhost:5180/end so the end-session flow can be exercised.
        await page.goto("http://localhost:5180/end")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'End for now' button to begin ending the session.
        # End for now button
        elem = page.get_by_role("button", name="End for now")
        await elem.click(timeout=10000)
        
        # -> Scroll down to reveal the completion screen and confirm the 'Warm • Calm • Grounded' message is visible.
        await page.mouse.wheel(0, 300)
        
        # -> Click the 'No, thank you' button to skip saving a reflection and proceed to the completion screen.
        # No, thank you button
        elem = page.get_by_role("button", name="No, thank you")
        await elem.click(timeout=10000)
        
        # -> Scroll down to reveal the completion screen and confirm the 'Warm • Calm • Grounded' message is visible.
        await page.mouse.wheel(0, 300)
        
        # --> Assertions to verify final state
        
        # --> Completion screen is displayed (completion page shows the 'Begin when ready' control).
        await page.get_by_role("button", name="Begin when ready").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The 'Begin when ready' button is visible on the completion screen.
        await expect(page.get_by_role("button", name="Begin when ready").nth(0)).to_be_visible(timeout=15000), "The 'Begin when ready' button is visible on the completion screen."
        
        # --> A warm completion message 'Warm • Calm • Grounded' is visible on the completion screen.
        # Assert-outcome: passed
        # Assert: The page displays the warm completion message 'Warm • Calm • Grounded'.
        await expect(page.locator("xpath=/html/body/div/div[1]/main/div[2]/div[3]/div/svg").nth(0)).to_contain_text("Warm \u2022 Calm \u2022 Grounded", timeout=15000), "The page displays the warm completion message 'Warm \u2022 Calm \u2022 Grounded'."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    