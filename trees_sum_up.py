import json
import csv
import statistics
import landsat8
import geopandas as gpd
from shapely.geometry import Polygon

MAX_CLOUD_COVER = 3
MIN_MONTH = 5
MAX_MONTH = 9
MAX_PIXELS = 100

def is_valid_item(link):
    if link["rel"] == "item":
        month = int(link["href"][5:7])
        return month >= MIN_MONTH and month <= MAX_MONTH
    return False

if __name__ == "__main__":
    df_shp = gpd.read_file("src/WRS2_descending_0/WRS2_descending.shp")

    with open("data/A45_trees.json", encoding="utf-8") as f:
        trees = json.load(f)

    with open('data/A45-19_values.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        for tree in trees:
            band_values = [[], [], [], [], [], [], [], []]
            filled = False
            with open("data/A45-19_{id}.geojson".format(id=tree), encoding="utf-8") as f:
                geojson = json.load(f)
                features = geojson["features"]
            print(tree)
            for feature in features:
                props = feature["properties"]
                if not props["A45_025"] in ["単", "竹林"] or props["A45_027"] < 0.1:
                    continue  # 樹種の条件

                try:
                    scenes = landsat8.get_pathrow(Polygon(feature["geometry"]["coordinates"][0]))  # シーンの条件1
                except Exception as e:
                    scenes = []

                for scene in scenes:
                    catalog = landsat8.get_catalog(scene["path"], scene["row"])
                    item_links = list(
                        filter(is_valid_item, catalog["links"]))
                    
                    for item_link in item_links:
                        item = landsat8.get_item(scene["path"], scene["row"],
                                        item_link["href"])
                        item_props = item["properties"]
                        cloud_cover = item_props["eo:cloud_cover"]
                        if cloud_cover > MAX_CLOUD_COVER:
                            continue # シーンの条件2

                        try:
                            mask_polygon = gpd.GeoDataFrame(crs={'init': 'epsg:4326'}, geometry=[scene["intersect"]])  # すべてPolygonの想定
                            values = landsat8.sum_up(item, mask_polygon, max_len=MAX_PIXELS)
                            check = 0
                            for i in range(len(band_values)):
                                band_values[i].extend(values[i])
                                if len(band_values[i]) >= MAX_PIXELS:
                                    band_values = band_values
                                    check += 1

                            if len(band_values) <= check:
                                filled = True
                                break
                        except Exception as e:
                            print(tree, e)
                    else:
                        continue
                    break
                else:
                    continue
                break
            if filled:
                mean = [statistics.mean(values[:MAX_PIXELS]) for values in band_values]
                variance = [statistics.variance(values[:MAX_PIXELS]) for values in band_values]
                writer.writerow([tree] + mean + variance)

