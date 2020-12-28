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
            poem = [random.choice(self.five), random.choice(self.seven), random.choice(self.five)]
            if self._judgment_connection("".join(poem)):
                poem_text = " ".join(poem)
            roop += 1

        return poem_text


if __name__ == '__main__':
    cp = ComposePoem()
    for _ in range(10):
        print(cp.compose())
