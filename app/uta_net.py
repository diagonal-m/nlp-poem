"""
Uta-Netから歌詞情報を収集するためのスクリプト
"""
import os
import pickle
from time import sleep

import requests
from bs4 import BeautifulSoup

from consts import BASE_URL, ARTIST_URL, LYRICS_DIR, LYRICS_FILE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_soup(url: str) -> BeautifulSoup:
    """
    urlを受け取りsoupを返す
    @param url: 対象のurl文字列
    @return: BeautifulSoup
    """
    # resquestsのレスポンスオブジェクトを取得
    response = requests.get(url)
    # ステータスコードが200番台以外はエラー
    response.raise_for_status()

    # 文字化けが起こらないようにコンテンツ取得
    response.encoding = response.apparent_encoding
    # レスポンスのHTMLからBeautifulSoupのオブジェクトを作る
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


class UtaNet:

    def __init__(self, base_url: str):
        """
        初期化メソッド
        """
        self.base_url = base_url
        # artist番号
        self.artist_nums = [126, 7424, 9283, 8722]
        self.song_urls: list = list()  # 曲URLを格納するリスト
        self.lyrics: list = list()  # 歌詞文字列を格納するリスト

    def _get_song_urls(self) -> None:
        """
        曲URLを取得するメソッド
        """
        for num in self.artist_nums:
            soup = get_soup(self.base_url.format(num))
            # 歌テーブルを取得
            song_tables = soup.find_all('table')
            # 曲URLを取得
            for song_table in song_tables:
                self.song_urls.extend(
                    [BASE_URL + song.find('a').attrs['href'] for song in song_table.find_all('td', class_='side td1')]
                )

    def _get_lyrics(self) -> None:
        """
        歌詞を取得するためのメソッド
        """
        for song_url in self.song_urls:
            soup = get_soup(song_url)
            self.lyrics.append(
                soup.find('div', id='kashi_area').text.replace('\u3000', ' ')
            )
            sleep(3)

    def exec_uta_net(self):
        """
        UtaNetクラスのメイン関数
        """
        # 全曲のURLを取得
        self._get_song_urls()
        # 歌詞を取得
        self._get_lyrics()

        # 歌詞情報を格納するディレクトリを作成
        dir_path = os.path.join(BASE_DIR, LYRICS_DIR)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # 歌詞のリストをpickleとして保存
        with open(os.path.join(dir_path, LYRICS_FILE), 'wb') as ly:
            pickle.dump(self.lyrics, ly)


if __name__ == '__main__':
    uta_net = UtaNet(BASE_URL + ARTIST_URL)
    uta_net.exec_uta_net()
