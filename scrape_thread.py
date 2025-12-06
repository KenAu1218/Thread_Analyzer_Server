import json
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
from analysis_sentiment import analyze_sentiment_advanced


def parse_thread(data: dict) -> dict:
    result = jmespath.search(
        """{
        text: post.caption.text,
        taken_at: post.taken_at,
        id: post.id,
        pk: post.pk,
        code: post.code,
        username: post.user.username,
        user_pic: post.user.profile_pic_url,
        user_verified: post.user.is_verified,
        reply_count: view_replies_cta_string,
        like_count: post.like_count,
        carousel_images: post.carousel_media[].image_versions2.candidates[1].url,
        single_image: post.image_versions2.candidates[1].url,
        giphy_image: post.giphy_media_info.images.fixed_height.url || post.giphy_media_info[].images.fixed_height.url || post.giphy_media_info.images[].fixed_height.url || post.giphy_media_info[].images[1].fixed_height.url,
        videos: post.video_versions[].url,
        reply_to_author_name: post.text_post_app_info.reply_to_author.username,
        is_reply: post.text_post_app_info.is_reply
    }""",
        data,
    )


    carousel = result.get("carousel_images")
    single = result.get("single_image")
    giphy = result.get("giphy_image")

    if carousel:
        result["images"] = carousel
    elif single:
        result["images"] = [single]
    else:
        result["images"] = []

    result.pop("carousel_images", None)
    result.pop("single_image", None)

    if giphy:
        result["gifImages"] = [giphy]
    result.pop("giphy_image", None)

    if result.get("videos"):
        result["images"] = []

    result["videos"] = list(set(result.get("videos") or []))
    result["url"] = f"https://www.threads.net/@{result.get('username')}/post/{result.get('code')}"
    result["sentiment"] = analyze_sentiment_advanced(result.get("text"))

    return result


def scrape_thread(url: str) -> dict:
    """Scrape Threads post using aggressive resource blocking"""
    try:
        last_part = url.strip("/").split("/")[-1]
        post_code = last_part.split("?")[0]
    except IndexError:
        raise ValueError(f"Could not extract post code from URL: {url}")

    with sync_playwright() as pw:
        # Launch headless (invisible)
        browser = pw.chromium.launch(headless=True)

        # Set a realistic viewport so Threads doesn't think we are a bot/mobile
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # ---------------------------------------------------------
        # THE BLOCKING LOGIC
        # We allow: 'document' (HTML), 'script' (JS), 'xhr', 'fetch' (Data)
        # We block: Everything visual.
        # ---------------------------------------------------------
        excluded_resource_types = ["image", "media", "font", "stylesheet", "other"]

        def block_aggressively(route):
            if route.request.resource_type in excluded_resource_types:
                # print(f"Blocking: {route.request.resource_type}") # Uncomment to debug
                route.abort()
            else:
                route.continue_()

        page.route("**/*", block_aggressively)
        # ---------------------------------------------------------

        print(f"Navigating to URL: {url}")

        # domcontentloaded is enough. We don't need 'networkidle' (too slow).
        page.goto(url, wait_until="domcontentloaded", timeout=15000)

        # OPTIMIZATION: Don't wait for the visual Link (<a>).
        # Wait directly for the DATA script.
        # Since we blocked CSS, the visual link might look weird or not render,
        # but the <script> tag is always there.
        print(f"Waiting for data script...")
        try:
            # We wait specifically for the JSON script tag
            page.wait_for_selector('script[type="application/json"][data-sjs]', state="attached", timeout=10000)
        except Exception:
            print("Warning: Timeout waiting for selector, attempting to parse anyway...")

        print("Parsing page content...")

        # We don't need to visually interact, so we just grab the HTML text
        html_content = page.content()
        selector = Selector(text=html_content)

        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()

        for hidden_dataset in hidden_datasets:
            if "thread_items" not in hidden_dataset:
                continue

            if f'"code":"{post_code}"' in hidden_dataset:
                print("Found correct data block.")
                data = json.loads(hidden_dataset)
                thread_items = nested_lookup("thread_items", data)

                if not thread_items:
                    continue

                threads = [parse_thread(t) for thread in thread_items for t in thread]

                # 1. Find Main Thread
                main_thread = next((t for t in threads if t.get("code") == post_code), None)

                replies = []

                # 2. Find Replies
                if main_thread:
                    op_username = main_thread.get('username')
                    for t in threads:
                        if t.get("code") == post_code:
                            continue
                        if (t.get("is_reply") is True and
                                t.get("reply_to_author_name") == op_username):
                            replies.append(t)

                    print(f"Found {len(replies)} replies.")
                    return {
                        "thread": main_thread,
                        "replies": replies,
                    }

                print(f"Main thread with code {post_code} not found.")
                return None

        raise ValueError(f"Could not find thread data for post code {post_code}")