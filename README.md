# 衛星画像から教師データを作ってみる

## 樹種判定
1. srcを作る
1. srcに[国有林野](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A45.html)全都道府県ポリゴンのgeojsonをダウンロード
1. `pipenv run python trees_split.py`で受取毎に分割
1. Landsat-8 の[path/row定義ファイル](https://www.usgs.gov/core-science-systems/nli/landsat/landsat-shapefiles-and-kml-files)をsrcにダウンロード
1. `pipenv run python trees_sum_up.py`を実行し、樹種ごとの特徴ベクトル生成


