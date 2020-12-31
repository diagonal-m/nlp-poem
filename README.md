# nlp-poem

　好きなアーティスト4組の全450曲を形態素解析して５調と７調の歌詞を収集する。ランダムに組み合わせたものの中で**係受けが成立しているもの**のみを抽出して返す。



## 使い方

```bash
$ git clone https://github.com/diagonal-m/nlp-poem.git
$ cd nlp-poem
$ docker build -f docker/Dockerfile -t nlp-poem --no-cache . 
$ docker run nlp-poem:latest  # 実行 - 川柳が10個生成される
```



## 生成結果

- 夢を見て ねえどうしても 僕たちは
- 正しさを 探してる音 幻覚か
- 嘆いても 笑っているよ 朝焼けに
- 不登校 どこであろうと ケンカする
- 間違いも 耐え忍ぶよう 君は立つ
- 蝉の音 光となって 落とされた
- 村人A 愛せた時に 笑うから
- 青い春 いつかさよなら クレヨンで
- へつらいも 残していこう 青い春
- 悔しさも 現実逃避 生き抜いた



## ディレクトリ構成

```bash
nlp-poem/
 ├── app/
 |    ├── lyrics/
 |    |    └── lyrics.pickle  # 歌詞データ
 |    ├── compose_poem.py  # 川柳生成スクリプト
 |    ├── consts.py  # 定数配置用
 |    └── uta_net.py  # uta-netから歌詞を収集するためのスクリプト
 ├── docker/
 |    ├── Dockerfile
 |    └── requirements.txt
 └── README.md
```



## 生成アルゴリズム

![図1](/Users/taichi/Desktop/図1.png)



## MeCabで形態素解析

 「形態素解析(Morphological Analysis)」とは、自然言語処理分野で主に事前処理として用いられる手法であり、対象となる言語の文法や単語の品詞情報をもとに、文章を形態素(単語が意味を持つ最小の単位)に分解する解析を指す。例えば、「すもももももももものうち」を形態素解析であるMeCabで解析すると「すもも も もも も もも の うち」に分解される。形態素解析器は、自身の参照する辞書より単語の品詞情報を取得して文字列を解析する。辞書には単語の品詞情報が含まれているが、辞書間で単語の種類や品詞情報が共通化されているわけではない。つまり、別の辞書を使用するとまったく別の品詞情報を用いていることと同じになるため、形態素解析結果が異なる可能性がある。

　Mecabは京都大学情報学研究科と日本電信電話株式会社コミュニケーション科学基礎研究所の共同研究で開発された形態素解析エンジンである．
言語，辞書，コーパス(データベース化されている言語資料)に依存しない汎用的な設計方針を採用しており，C言語，C++，Java，python等，数多くの言語で使用することが可能である．また，設定することで様々な辞書を用いることが可能なため，日本語の形態素解析エンジンの中では最もよく使用されている。

## CaboChaで係受け解析

　CaboChaはSVM(Support Vector Machines)に基づく係り受け解析器で、係受け解析は文節間の「修飾する(係る)」「修飾される(受ける)」の関係を調べる事。



## 係受け判定あり VS 係受け判定なし

| 係受け判定あり                     | 係受け判定なし                       |
| ---------------------------------- | ------------------------------------ |
| さようなら 物質主義 望まない       | 蝉の音 負けないように ありもせず     |
| 泣いた事 開けないままで 愛なんて   | 羽ばたいて 隠れてないで 地平線       |
| 泣いた事 全ての日々を さようなら   | あなたでも ただ降り落ちた 結末は     |
| 気付かずに 高鳴る胸が わかってた   | 知りながら わかって欲しい 青い春     |
| 振り向けぬ 才能不在 メロディー     | 1日分 旅立った唄 こりもせず          |
| ひとつだけ わかって欲しい 信じるよ | 風の街 雨は気まぐれ 温もりが         |
| さあどうぞ 死なない為に 落ち込んで | 聞き慣れた 言うもんだから 無いモノで |
| 海が凪ぎ 戦っていた 出てこいよ     | 苦しんで 探し続ける 拾うタメ         |
| 星殺し 願っていたい 君は立つ       | メロディー イツモアナタノ 縷々として |
| そうだった 息を止めてた 虚しくて   | 思うけど 戦っていた 愛しさも         |



## 考察

　係受け判定ありの川柳を係受け判定なしの川柳を比較すると、単純な言葉の羅列であったりと意味の通らないものが出力される割合が少なくなったため、導入した係り受け判定は一定の効果はあった。

　ただ現状でも意味の通る川柳は10分の１程度の割合での出力なため、係受け判定の精度を向上させるか別の方法を考える必要がある。



## ソースコード

*uta_net.py*

```python
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

```

*compose_poem.py*

```python
"""
川柳を作成するスクリプト
"""
import os
import re
import pickle
import random

import MeCab
import CaboCha

from consts import LYRICS_DIR, LYRICS_FILE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ComposePoem:
    """
    川柳作成クラス
    """
    def __init__(self):
        """
        初期化関数
        """
        self.m = MeCab.Tagger("-Ochasen")
        self.c = CaboCha.Parser()
        with open(os.path.join(BASE_DIR, LYRICS_DIR, LYRICS_FILE), 'rb') as f:
            self.lyric_list = pickle.load(f)
        self.five = list()
        self.seven = list()

    def _extraction_five_or_seven(self) -> None:
        """
        5音と7音のものを抽出する
        """
        lyric_dict = dict()
        for lyric in self.lyric_list:
            for ly in lyric.split():
                morphed = [re.split(r"[,\t\s\n]", w) for w in self.m.parse(ly.split()[0]).split("\n")]
                morphed.remove([""])
                morphed.remove(["EOS"])
                k = [morph[1] if morph[1] != "*" else morph[0] for morph in morphed]
                lyric_dict[ly] = "".join(k)

        for k, v in lyric_dict.items():
            if len(v) == 5:
                self.five.append(k)
            if len(v) == 7:
                self.seven.append(k)

    def _judgment_connection(self, text: str) -> bool:
        """
        係受けが成立しているかどうかを判定する
        @param text: 文字列
        @return: 係受けが成立しているかどうかのbool値
        """
        tree = self.c.parse(text)
        # 形態素を結合しつつ[{c:文節, to:係り先id}]の形に変換する
        chunks = list()
        text = ""
        toChunkId = -1
        for i in range(0, tree.size()):
            token = tree.token(i)
            text = token.surface if token.chunk else (text + token.surface)
            toChunkId = token.chunk.link if token.chunk else toChunkId
            # 文末かchunk内の最後の要素のタイミングで出力
            if i == tree.size() - 1 or tree.token(i + 1).chunk:
                chunks.append({'c': text, 'to': toChunkId})

        # 係り元→係り先の形式でリストを作成
        connections = list()
        for chunk in chunks:
            if chunk['to'] >= 0:
                connections.append([chunk['c'], chunks[chunk['to']]['c']])

        # 係受けが成立しているか否かを返す
        for c_1, c_2 in zip(connections[:-1], connections[1:]):
            if c_1[-1] != c_2[0]:
                return False

        return True

    def compose(self) -> str:
        """
        係受けの成立した5-7-5の川柳文字列を返す関数
        @return: 川柳文字列
        """
        roop = 0
        max_iter = 1000
        poem_text = ''

        self._extraction_five_or_seven()

        while not poem_text or roop == max_iter:
            poem = [random.choice(self.five), 
                    random.choice(self.seven), 
                    random.choice(self.five)]
            if self._judgment_connection("".join(poem)):
                poem_text = " ".join(poem)
            roop += 1

        return poem_text


if __name__ == '__main__':
    cp = ComposePoem()
    for _ in range(10):
        print(cp.compose())

```

*consts.py*

```python
"""
定数配置ファイル
"""
BASE_URL = "https://www.uta-net.com"
ARTIST_URL = "/artist/{}/"

LYRICS_DIR = 'lyrics'
LYRICS_FILE = 'lyrics.pickle'
```

