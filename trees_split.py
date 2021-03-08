import json

if __name__ == "__main__":
    with open("data/A45_trees.json", encoding="utf-8") as f:
        trees = json.load(f)

    prefectures = range(1, 48)  # 実行したい都道府県のIDの配列
    for tree in trees:
        features = []
        for id in prefectures:
            prefecture_id = str(id).zfill(2)
            try:

                src_path = "src/A45-19_{id}.geojson".format(id=prefecture_id)
                
                with open(src_path) as f:
                    src = json.load(f)
                    for feature in src["features"]:
                        if feature["properties"]["A45_015"] == tree:
                            features.append(feature)
            except Exception as e:
                print(prefecture_id, e)
        dst_path = "data/A45-19_{id}.geojson".format(id=tree)
        export_geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(dst_path, "w", encoding="utf-8") as f:
            json.dump(export_geojson, f, indent=4, ensure_ascii=False)
        print("done: " + tree)