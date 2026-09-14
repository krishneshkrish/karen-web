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
        
        # -> Navigate to the chat page (open http://localhost:5180/chat) so the chat UI can be tested.
        await page.goto("http://localhost:5180/chat")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Reload the chat page by navigating to http://localhost:5180/chat so the chat UI can render.
        await page.goto("http://localhost:5180/chat")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Navigate to the site root (http://localhost:5180) to reload the SPA and trigger the chat UI to render.
        await page.goto("http://localhost:5180")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Open the chat page by navigating to http://localhost:5180/chat so the chat UI can render.
        await page.goto("http://localhost:5180/chat")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Navigate to the site root (http://localhost:5180) to reload the SPA and attempt to trigger the chat UI to render.
        await page.goto("http://localhost:5180")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Open the chat page (http://localhost:5180/chat) and wait for the chat UI to render so the crisis overlay flow can be tested.
        await page.goto("http://localhost:5180/chat")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Type a crisis-related message into the message composer labeled 'Type when you're ready...' and submit it by clicking the 'Begin when ready' button.
        # Type when you're ready... text area
        elem = page.get_by_role("textbox", name="Type when you're ready...")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("I'm feeling overwhelmed and having thoughts of harming myself \u2014 I need help right now.")
        
        # -> Type a crisis-related message into the message composer labeled 'Type when you're ready...' and submit it by clicking the 'Begin when ready' button.
        # Begin when ready button
        elem = page.get_by_role("button", name="Begin when ready")
        await elem.click(timeout=10000)
        
        # -> Click the 'End session' button to dismiss the crisis support overlay.
        # End session button
        elem = page.get_by_role("button", name="End session")
        await elem.click(timeout=10000)
        
        # -> Click the 'End for now' button to dismiss the crisis support overlay.
        # End for now button
        elem = page.get_by_role("button", name="End for now")
        await elem.click(timeout=10000)
        
        # -> Click the 'No, thank you' button to dismiss the reflection modal and return to the chat session view.
        # No, thank you button
        elem = page.get_by_role("button", name="No, thank you")
        await elem.click(timeout=10000)
        
        # -> Click the 'Chat' button (label: Chat) to open the chat session view and check that the message composer is available.
        # New chat session button
        elem = page.get_by_role("button", name="New chat session")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The app did not return to the chat session screen after dismissing the crisis overlay.
        # Assert-outcome: failed
        # Assert: Expected the URL to contain '/chat' indicating the chat session screen.
        await expect(page).to_have_url(re.compile("/chat"), timeout=15000), "Expected the URL to contain '/chat' indicating the chat session screen."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    