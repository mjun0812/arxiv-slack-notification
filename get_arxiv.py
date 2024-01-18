import datetime
import json
import os
from pprint import pformat

import deepl
import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()


def translate_gcp(text):
    try:
        res = requests.post(
            f"https://translation.googleapis.com/language/translate/v2?key={os.getenv('GCP_API_KEY')}",
            json={"q": text, "target": "ja"},
        )
        result = res.json()["data"]["translations"][0]["translatedText"]
    except Exception as e:
        print(f"GCP: {e}")
        result = ""
    return result


def translate_deepl(text):
    try:
        translator = deepl.Translator(os.getenv("DEEPL_TOKEN"))
        result = translator.translate_text(text, target_lang="JA")
    except Exception as e:
        print(f"DeepL: {e}")
        result = ""
    return result


def get_arxiv(keyword, category, max_results=20):
    keyword = keyword.replace(" ", "+")
    feed = feedparser.parse(
        f"http://export.arxiv.org/api/query?search_query=all:{keyword}"
        f"+AND+cat:{category}&max_results={max_results}&sortBy=submittedDate"
    )
    return feed


def post_slack(channel="#通知", username="通知", message=""):
    response = requests.post(
        os.getenv("SLACK_WEBHOOK"),
        headers={"Content-Type": "application/json"},
        json={
            "channel": channel,
            "text": message,
            "username": username,
            "icon_emoji": ":ghost:",
        },
    )
    return response.status_code


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("./.cache", exist_ok=True)

    with open("config.json") as f:
        config = json.load(f)
    print(config)

    translators = {
        "DeepL": translate_deepl,
        "Google": translate_gcp,
        "None": lambda x: x,
    }

    results = {}
    for query in config["keywords"]:
        key = query["keyword"].lower().replace(" ", "_")
        result = get_arxiv(
            keyword=f"%22{query['keyword']}%22",
            category=query["category"],
            max_results=query["max_results"],
        )
        if result["status"] != 200:
            continue

        # Check cache
        if os.path.exists(f"./.cache/{key}.json"):
            with open(f"./.cache/{key}.json") as f:
                cache = json.load(f)
            cache_title_list = [paper["title"] for paper in cache]
        else:
            cache = []
            cache_title_list = []

        # parse
        num_new_paper = 0
        for res in result["entries"]:
            paper = {
                "title": res["title"].replace("\n", ""),
                "abstruct": "".join(res["summary"].replace("\n", "")),
                # "authors": ", ".join([author["name"] for author in res["authors"]]),
                "url": res["link"],
                "date": res["published"],
            }
            if paper["title"] in cache_title_list:
                continue
            num_new_paper += 1

            abst = ""
            for translator_name in config["translators"]:
                translated_abst = translators[translator_name](paper["abstruct"])
                if translated_abst:
                    abst = f"{translated_abst}\nTranslate by {translator_name}"
                    break

            post_slack(
                channel="#paper",
                username=key,
                message=(
                    f"【タイトル】: {paper['title']}\n"
                    # f"【著者】: {paper['authors']}\n"
                    f"【Keyword】: {key}\n"
                    f"【URL】: {paper['url']}\n"
                    f"【Date】{paper['date']}\n"
                    f"【Fetch Date】{now}\n"
                    f"【Abst】: {abst}\n"
                    f"【Abst_en】: {paper['abstruct']}\n"
                ),
            )

        with open(f"./.cache/{key}.json", "w") as f:
            json.dump(cache, f, indent=2)
        results[key] = num_new_paper

    # Send All Result
    post_slack(
        channel="#paper",
        username="Paper Stats",
        message="【New paper】\n" + pformat(results, indent=2),
    )


if __name__ == "__main__":
    main()
