# coding=utf-8
import os
import requests
import pandas as pd

JA_URL_PREFIX = 'http://2018.scalamatsuri.org/ja/candidates'
EN_URL_PREFIX = 'http://2018.scalamatsuri.org/en/candidates'

from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def find_cfp_name(directory):
    """
    ディレクトリからCfP応募リストを取得する
    """

    for root, dirs, files in os.walk(directory):
        for file in files:
            name, _ = os.path.splitext(file)
            yield name


def count_b_hatena(name):
    """
    はてなブックマークの件数を取得する
    """

    endpoint = 'http://api.b.st-hatena.com/entry.count'
    target_ja_url = f'{JA_URL_PREFIX}/{name}/'
    target_en_url = f'{EN_URL_PREFIX}/{name}/'
    urls = [target_ja_url, target_en_url]

    result = [name]
    for url in urls:
        p = {'url': url}
        response = requests.get(endpoint, params=p)
        count = 0
        if response.text:
            count = int(response.text)

        result.append(count)

    return result


def count_tweet(name):
    """
    ツイートの件数を取得する
    """

    endpoint = 'http://jsoon.digitiminimi.com/twitter/count.json'
    target_ja_url = f'{JA_URL_PREFIX}/{name}/'
    target_en_url = f'{EN_URL_PREFIX}/{name}/'
    urls = [target_ja_url, target_en_url]

    result = [name]
    for url in urls:
        p = {'url': url}
        response = requests.get(endpoint, params=p)
        json = response.json()
        #         print(json)

        result.append(json['count'])
    return result


def count_fb_v28_like(name):
    """
    facebookのいいねの件数を取得する
    画面上の数字がv2.8のものと同一だったため採用
    """

    endpoint = 'https://graph.facebook.com/v2.8/'
    target_ja_url = f'{JA_URL_PREFIX}/{name}/'
    target_en_url = f'{EN_URL_PREFIX}/{name}/'
    token = os.environ.get('FB_ACCESS_TOKEN')

    urls = [target_ja_url, target_en_url]

    result = [name]
    for url in urls:
        p = {'fields': 'og_object{engagement}', 'id': url, 'access_token': token}
        response = requests.get(endpoint, params=p)
        json = response.json()
        #         print(json)

        reaction_count = 0
        if 'og_object' in json:
            reaction_count = json['og_object']['engagement']['count']

        result.append(reaction_count)

    return result


def count_fb_v28_share(name):
    """
    facebookのシェアの件数を取得する
    画面上の数字がv2.8のものと同一だったため採用
    """

    endpoint = 'https://graph.facebook.com/v2.8/'
    target_ja_url = f'{JA_URL_PREFIX}/{name}/'
    target_en_url = f'{EN_URL_PREFIX}/{name}/'
    token = os.environ.get('FB_ACCESS_TOKEN')

    urls = [target_ja_url, target_en_url]

    result = [name]
    for url in urls:
        p = {'fields': 'share', 'id': url, 'access_token': token}
        response = requests.get(endpoint, params=p)
        json = response.json()
        #         print(json)

        share_count = 0
        if 'share' in json:
            share_count = json['share']['share_count']

        result.append(share_count)

    return result


def extract_to_dataframe(path):
    """
    各APIに問い合わせ、件数を取得したものを、集約してDataFrameへ変換する
    """

    logger.info(f'path: {path}')

    tweets = []
    hatena_bs = []
    fb_likes = []
    fb_shares = []

    for name in find_cfp_name(path):
        logger.info(f'extract: {name}')

        tweets.append(count_tweet(name))

        hatena_bs.append(count_b_hatena(name))

        fb_likes.append(count_fb_v28_like(name))

        fb_shares.append(count_fb_v28_share(name))

    df_t = pd.DataFrame(tweets, columns=['name', 'ja_tw', 'en_tw'])
    df_h = pd.DataFrame(hatena_bs, columns=['name', 'ja_hatena', 'en_hatena'])

    df_fb_l = pd.DataFrame(fb_likes, columns=['name', 'ja_like', 'en_like'])
    df_fb_s = pd.DataFrame(fb_shares, columns=['name', 'ja_share', 'en_share'])
    df_fb = pd.merge(df_fb_l, df_fb_s)
    # columnの位置の調整
    df_fb[['name', 'ja_like', 'ja_share', 'en_like', 'en_share']]

    # tweet, facebook, はてブの順に表示する
    merged = df_t.merge(df_fb).merge(df_h)

    return merged


def execute():
    path = '/app/_candidates_ja'
    csv_file = '/app/work/social_count.csv'

    df = extract_to_dataframe(path)

    logger.info(f'csv: {csv_file}')
    df.to_csv(csv_file)


if __name__ == '__main__':
    execute()
