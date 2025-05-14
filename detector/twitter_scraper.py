from scrapfly import ScrapflyClient, ScrapeConfig
from bs4 import BeautifulSoup
from detector.bio_analysis import analyze_bio
from datetime import datetime

client = ScrapflyClient(key="scp-live-9a9eaa9369bd441a8053fe120294c4d3")

def get_user_profile(username):
    url = f"https://x.com/{username}"

    try:
        result = client.scrape(ScrapeConfig(url=url, asp=True))
        soup = BeautifulSoup(result.content, 'lxml')

        # Extract bio from meta tag
        meta_desc = soup.find("meta", {"name": "description"})
        bio_text = meta_desc["content"] if meta_desc else ""

        # Dummy values for now (real scraping needs JS rendering)
        followers = 150  # You can hardcode for now until you use Twitter API or Selenium
        following = 80
        profile_picture = f"https://x.com/{username}/photo"  # placeholder
        account_creation_date = "2024-12-10"  # placeholder

        profile_data = {
            "username": username,
            "profile_url": url,
            "bio_analysis": analyze_bio(bio_text),  # pass string, not soup
            "followers": int(followers),
            "following": int(following),
            "profile_picture": profile_picture,
            "account_creation_date": account_creation_date
        }

        return profile_data

    except Exception as e:
        print(f"Error occurred while fetching profile: {e}")
        return None
