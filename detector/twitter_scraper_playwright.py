from playwright.sync_api import sync_playwright
import time
import random


def get_user_profile(username):
    with sync_playwright() as p:
        # Configure browser to mimic human
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        page = context.new_page()

        try:
            # Random delays to avoid detection
            time.sleep(random.uniform(1, 3))

            url = f"https://x.com/{username}"
            page.goto(url, timeout=30000)

            # Wait for critical elements
            page.wait_for_selector('article', timeout=10000)

            # Check for account issues
            if page.locator('text=Account suspended').count() > 0:
                return None
            if page.locator('text=doesn\'t exist').count() > 0:
                return None

            # Extract bio - NEW IMPROVED METHOD
            bio = ""
            bio_element = page.locator('[data-testid="UserDescription"]').first
            if bio_element.count() > 0:
                bio = bio_element.inner_text()

            # EXTRACT FOLLOWERS/FOLLOWING - RELIABLE METHOD
            def extract_count(text):
                if 'K' in text:
                    return int(float(text.replace('K', '')) * 1000)
                elif 'M' in text:
                    return int(float(text.replace('M', '')) * 1000000)
                return int(text.replace(',', ''))

            followers = extract_count(
                page.locator('a[href*="/followers"] span').first.inner_text()
            )
            following = extract_count(
                page.locator('a[href*="/following"] span').first.inner_text()
            )

            # Get profile picture
            img = page.locator('img[alt*="profile photo"]').first
            profile_pic = img.get_attribute('src') if img.count() > 0 else ""

            return {
                "username": username,
                "bio": bio,
                "followers": followers,
                "following": following,
                "profile_picture": profile_pic,
                "account_creation_date": "Unknown"  # Still requires login
            }

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            return None
        finally:
            browser.close()