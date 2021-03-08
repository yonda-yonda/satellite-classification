import json
import csv

if __name__ == "__main__":
    with open("data/A45_trees.json", encoding="utf-8") as f:
        trees = json.load(f)
    with open('data/A45-19_count.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "count", "area", "monotone_count", "monotone_area", "over_pixel_count", "over_pixel_area", "satisfied_count", "satisfied_area"])
        for tree in trees:
            with open("data/A45-19_{id}.geojson".format(id=tree), encoding="utf-8") as j:
                geojson = json.load(j)

                d = [tree, len(geojson["features"]), 0,0,0,0,0,0,0]
                for feature in geojson["features"]:
                    props = feature["properties"]
                    d[2] += props["A45_027"]
                    if props["A45_025"] in ["単", "竹林"]:
                        d[3] += 1
                        d[4] += props["A45_027"]
                    if props["A45_027"]>= 0.1:
                        d[5] += 1
                        d[6] += props["A45_027"]
                    if props["A45_025"] in ["単", "竹林"] and props["A45_027"]>= 0.1:
                        d[7] += 1
                        d[8] += props["A45_027"]
                writer.writerow(d)
