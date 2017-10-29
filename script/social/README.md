SNS拡散度合いカウントツール
==========================

## requirement

* docker
* docker-compose
* facebookのAPI ACCESS TOKEN
    * https://developers.facebook.com/docs/facebook-login/access-tokens/?locale=ja_JP
    * 取得したら、 `fb.env`に以下のように記載する

### fb.env

```ini
FB_ACCESS_TOKEN=<取得したトークン>
```

## usage

### build

まずはじめにbuildしてください。

`count.py` を修正した場合も、buildしてください。

```sh
docker-compose build
```

### run

実行する

```sh
docker-compose run --rm social
```

`script/social_count.csv` が出力されていれば、成功です
