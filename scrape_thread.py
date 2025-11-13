import base64
import os
import json
from typing import Dict, List

import requests

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright, TimeoutError
from analysis_sentiment import analyze_sentiment_advanced


def parse_thread(data: Dict) -> Dict:
    """Parse Threads post JSON dataset for the most important fields"""
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
        giphy_image: post.giphy_media_info.images.fixed_height.url,
        videos: post.video_versions[].url,
        reply_to_author_name: post.text_post_app_info.reply_to_author.username,
        is_reply: post.text_post_app_info.is_reply
    }""",
        data,
    )

    if (result.get("username") == "charlieneiss"):
        print("charlieneiss: result", result)
        print("charlieneiss: ", result.get("images"))

    carousel = result.get("carousel_images")
    single = result.get("single_image")
    giphy = result.get("giphy_image")

    if carousel:
        result["images"] = carousel  # This is already a list
    elif single:
        result["images"] = [single]  # Wrap the single URL in a list
    else:
        result["images"] = []  # Default to an empty list

    # Clean up the temporary keys
    result.pop("carousel_images", None)
    result.pop("single_image", None)

    if giphy:
        result["gifImages"] = [giphy]
    result.pop("giphy_image", None)

    # If a post has a video, it is the primary media.
    # We clear the images array to avoid showing the static preview image.
    if result.get("videos"):
        result["images"] = []

    result["videos"] = list(set(result.get("videos") or []))

    result["url"] = f"https://www.threads.net/@{result.get('username')}/post/{result.get('code')}"

    result["sentiment"] = analyze_sentiment_advanced(result.get("text"))

    # For image analysis ***********
    # image_urls = result.get("images") or []
    # result["image_descriptions"] = []
    # if image_urls:
    #     print(f"Found {len(image_urls)} images to analyze...")
    # for url in image_urls:
    #     description = analyze_image_content(url)
    # print(f"  - Description: {description}")
    # image_sentiment = analyze_sentiment_advanced(description)
    # print(f"  - Sentiment: {image_sentiment['label']}")
    # result["image_descriptions"].append({
    #     "url": url,
    #     "description": description,
    #     "sentiment": image_sentiment
    # })
    # For image analysis ***********
    return result


def scrape_thread(url: str) -> dict:
    """Scrape Threads post and replies from a given URL"""
    try:
        last_part = url.strip("/").split("/")[-1]
        post_code = last_part.split("?")[0]
    except IndexError:
        raise ValueError(f"Could not extract post code from URL: {url}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print(f"Navigating to URL: {url}")
        page.goto(url)

        print(f"Waiting for post '{post_code}' to appear...")
        page.wait_for_selector(f'a[href*="{post_code}"]')
        print("Post found. Parsing page content...")

        selector = Selector(page.content())
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

                print("thread_items", thread_items)
                threads = [parse_thread(t) for thread in thread_items for t in thread]

                # --- Step 1: Find the main thread first ---
                main_thread = next((t for t in threads if t.get("code") == post_code), None)

                replies = []

                # --- Step 2: If the main thread exists, find its direct replies ---
                if main_thread:
                    # Get the username of the main thread's author
                    op_username = main_thread.get('username')

                    # Iterate again to find only replies to the main thread
                    for t in threads:
                        # Skip the main thread itself
                        if t.get("code") == post_code:
                            continue

                        # Get the 'reply_to_author' object for checking
                        if (t.get("is_reply") is not None and t.get("reply_to_author_name") is not None and t.get(
                                "is_reply") is True and t.get("reply_to_author_name") == op_username):
                            replies.append(t)

                    # --- Step 3: Sort the filtered replies ---
                    # cant predict the sorting algorithm of facebook
                    # sort replies by taken_at
                    # replies.sort(
                    #     key=lambda r: (r.get('username') == op_username, r.get('taken_at', 0),
                    #                    ),
                    #     reverse=True
                    # )

                    print(f"Found and sorted {len(replies)} replies to the main thread.")
                    return {
                        "thread": main_thread,
                        "replies": replies,
                    }

                # Handle case where the main thread with 'post_code' was not found
                print(f"Main thread with code {post_code} not found.")
                return None  # Or {"thread": None, "replies": []}

        raise ValueError(f"Could not find thread data for post code {post_code} in the page")

# def get_image_as_base64(url: str) -> str:
#     """Downloads an image and returns it as a Base64 encoded string."""
#     if not url:
#         print("No URL provided.")
#         return None
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         response = requests.get(url, timeout=10, headers=headers)  # <-- Pass headers here
#         response.raise_for_status()
#         encoded_string = base64.b64encode(response.content).decode('utf-8')
#
#         print("encoded_string", encoded_string)
#         return f"data:{response.headers['Content-Type']};base64,{encoded_string}"
#         # Return a data URI which can be used directly in an <img> src attribute
#         return f"data:{response.headers['Content-Type']};base64,{encoded_string}"
#     except requests.exceptions.RequestException as e:
#         print(f"Could not fetch image from {url}: {e}")
#         return None
