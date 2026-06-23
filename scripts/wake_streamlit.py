"""Wake a sleeping Streamlit Community Cloud app.

A plain HTTP GET to a sleeping app returns the "Zzzz" interstitial page (HTTP 200)
but does NOT actually wake the container — the wake-up requires clicking the
"Yes, get this app back up!" button, which fires a JavaScript-driven request to
the Streamlit Cloud backend.

This script uses Playwright (headless Chromium) to:
  1) navigate to the app URL,
  2) detect & click the wake-up button if the app is asleep,
  3) wait until the real app shell renders (segmented nav present),
  4) exit 0 on success — never fail the CI job hard.

Run as:
    python scripts/wake_streamlit.py [URL]
"""
from __future__ import annotations

import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

DEFAULT_URL = "https://sm-dashboard.streamlit.app/"


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"[wake] target: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 oevk-keep-alive/1.0"
            ),
        )
        page = ctx.new_page()
        page.set_default_timeout(60_000)
        try:
            page.goto(url, wait_until="domcontentloaded")
            print("[wake] page loaded")
        except Exception as ex:
            print(f"[wake] goto failed: {ex}")
            browser.close()
            return 0

        # If asleep, Streamlit Cloud shows a button with this label (English UI).
        # The German Streamlit Cloud is the same label — the interstitial isn't localised.
        wake_clicked = False
        try:
            # Match the wake-up button by visible text — covers small wording variants.
            candidates = [
                "Yes, get this app back up!",
                "Yes, get this app back up",
                "get this app back up",
            ]
            for label in candidates:
                btn = page.get_by_role("button", name=label, exact=False).first
                try:
                    btn.wait_for(state="visible", timeout=4_000)
                except PWTimeout:
                    continue
                print(f"[wake] sleep-interstitial detected — clicking '{label}'")
                btn.click()
                wake_clicked = True
                break
            if not wake_clicked:
                print("[wake] no sleep-button visible (app likely already awake)")
        except Exception as ex:
            print(f"[wake] wake-button probe error: {ex}")

        # Wait for the real Streamlit app to render: presence of the segmented-nav
        # button group is a strong signal the Python rerun has reached the user.
        try:
            page.wait_for_selector(
                '[data-testid="stButtonGroup"] button',
                timeout=240_000 if wake_clicked else 30_000,
            )
            # small settle delay so traffic counters definitely register a session
            time.sleep(3)
            tabs = page.locator('[data-testid="stButtonGroup"] button').all_inner_texts()
            print(f"[wake] app rendered, nav tabs: {tabs}")
        except PWTimeout:
            print("[wake] app did not render in time — proceeding anyway")
        except Exception as ex:
            print(f"[wake] wait-for-app error: {ex}")

        browser.close()
    print("[wake] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
