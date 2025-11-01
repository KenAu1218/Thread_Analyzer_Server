import base64
import os
import json
from typing import Dict, List

import requests

from analysis_sentiment import analyze_sentiment_advanced

# FIX 1: Add this line to suppress the Hugging Face tokenizer warning.
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
# FIX 2: Import TimeoutError to handle cases where the popup doesn't appear.
from playwright.sync_api import sync_playwright, TimeoutError
# from analysis_sentiment import analyze_sentiment_advanced, analyze_image_content
from analysis_sentiment import analyze_sentiment_advanced


def parse_thread(data: Dict) -> Dict:
    """Parse Threads post JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        text: post.caption.text,
        published_on: post.taken_at,
        id: post.id,
        pk: post.pk,
        code: post.code,
        username: post.user.username,
        user_pic: post.user.profile_pic_url,
        user_verified: post.user.is_verified,
        user_pk: post.user.pk,
        user_id: post.user.id,
        has_audio: post.has_audio,
        reply_count: view_replies_cta_string,
        like_count: post.like_count,
        images: post.carousel_media[].image_versions2.candidates[1].url || [post.image_versions2.candidates[1].url],
        image_count: post.carousel_media_count,
        videos: post.video_versions[].url
    }""",
        data,
    )

    # --- NEW FIX STARTS HERE ---

    # 1. Filter out 'null' images from text-only posts
    if result.get("images"):
        result["images"] = [url for url in result["images"] if url]

    # 2. Prioritize video/GIFs to prevent duplicates
    # If a post has a video, it is the primary media.
    # We clear the images array to avoid showing the static preview image.
    if result.get("videos"):
        result["images"] = []

    # --- NEW FIX ENDS HERE ---

    result["videos"] = list(set(result.get("videos") or []))
    if result.get("reply_count") and not isinstance(result["reply_count"], int):
        reply_string = result["reply_count"].split(" ")[0]

        if reply_string.isdigit():
            result["reply_count"] = int(reply_string)
        else:
            result["reply_count"] = 0

    result["url"] = f"https://www.threads.net/@{result.get('username')}/post/{result.get('code')}"

    result["sentiment"] = analyze_sentiment_advanced(result.get("text"))

    # image_urls = result.get("images") or []
    # result["image_descriptions"] = []
    # if image_urls:
        # print(f"Found {len(image_urls)} images to analyze...")
        # for url in image_urls:
            # description = analyze_image_content(url)
            # print(f"  - Description: {description}")
            # image_sentiment = analyze_sentiment_advanced(description)
            # print(f"  - Sentiment: {image_sentiment['label']}")
            # result["image_descriptions"].append({
            #     "url": url,
                # "description": description,
                # "sentiment": image_sentiment
            # })

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

                threads = [parse_thread(t) for thread in thread_items for t in thread]

                main_thread = None
                replies = []
                for t in threads:
                    if t.get("code") == post_code:
                        main_thread = t
                    else:
                        replies.append(t)

                if main_thread:
                    op_username = main_thread.get('username')
                    replies.sort(
                        key=lambda r: (r.get('username') == op_username, r.get('like_count', 0),
                                       r.get('published_on', 0)),
                        reverse=True
                    )

                    print(f"Found and sorted {len(replies)} replies.")
                    return {
                        "thread": main_thread,
                        "replies": replies,
                    }

        raise ValueError(f"Could not find thread data for post code {post_code} in the page")


def get_image_as_base64(url: str) -> str:
    """Downloads an image and returns it as a Base64 encoded string."""
    if not url:
        print("No URL provided.")
        return None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)  # <-- Pass headers here
        response.raise_for_status()
        encoded_string = base64.b64encode(response.content).decode('utf-8')

        print("encoded_string", encoded_string)
        return f"data:{response.headers['Content-Type']};base64,{encoded_string}"
        # Return a data URI which can be used directly in an <img> src attribute
        return f"data:{response.headers['Content-Type']};base64,{encoded_string}"
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch image from {url}: {e}")
        return None
