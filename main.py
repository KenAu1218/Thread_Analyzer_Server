
import json

from scrape_thread import scrape_thread
from scrape_user_thread import scrape_profile

if __name__ == "__main__":
    try:
        scraped_data = scrape_thread("https://www.threads.net/t/C8H5FiCtESk/")
        print("--- Main Thread ---")
        print(json.dumps(scraped_data["thread"], indent=2))
        # print("\n--- Replies ---")
        # print(json.dumps(scraped_data["replies"], indent=2))
    except Exception as e:
        print(f"Error scraping single thread: {e}")

    print("\n" + "="*50 + "\n")

    # --- Example 2: Scrape a user's profile for all recent posts (new functionality) ---
    print("--- Running User Profile Scrape Example ---")
    try:
        profile_url = "https://www.threads.net/@zuck"
        user_posts = scrape_profile(profile_url)
        print(f"\n--- Scraped {len(user_posts)} total posts from {profile_url} ---")
        print(json.dumps(user_posts, indent=2))
    except Exception as e:
        print(f"Error scraping user profile: {e}")