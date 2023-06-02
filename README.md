# Arxiv Slack Notice

指定したキーワードで検索した最新論文を，Abstを和訳して毎日Slackに通知するスクリプト．

## Require

- Docker, Docker Compose
- DeelL or Google Cloud Translate APIのAPI Key
- SlackのWebhook URL

## Install

```bash
cp env.template .env
cp config.template.json config.json

docker compose build
docker compose up -d
```

- config.json

`translators`はDeepL, Google, None(翻訳なし)の中から選択できます．  
リストの順番に翻訳を試行し，最初に翻訳が成功したものが採用されます．  
下の例では，DeepL -> Googleの順に翻訳が施行され，DeepL翻訳が失敗(API rateなど)した場合は，
Google翻訳が試されます．
全て失敗した場合は英文をそのまま返します．

```js
{
    "translaters": [
        "DeepL",
        "Google",
        "None",
    ],
    "keywords": [
        {
            "keyword": "Transformer",
            "category": "cs.CV",
            "max_results": 20
        }
    ]
}
```

- .env

DEEP LとGoogle Translateのどちらかしか使わない場合は，片方だけ設定すれば良いです．

```bash
SLACK_WEBHOOK="https://...."
DEEPL_TOKEN=""
GCP_API_KEY=""
```

通知時間は`docker/cron.conf`から変更できます．
