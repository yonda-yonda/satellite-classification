import re
import requests
import rasterio
import math
import geopandas as gpd
from shapely.geometry import Polygon
from rasterio.mask import mask

base_path = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1"


def get_pathrow(target_polygon):
    df_shp = gpd.read_file("src/WRS2_descending_0/WRS2_descending.shp")
    filtered = df_shp[df_shp.geometry.intersects(target_polygon)]
    ret = []
    for i, row in filtered.iterrows():
        ret.append({
            'row': row.ROW,
            'path': row.PATH,
            'intersect': row.geometry.intersection(target_polygon)
        })
    return ret


def get_catalog(path, row):
    response = requests.get(
        "{}/{}/{}/catalog.json".format(base_path, str(path).zfill(3), str(row).zfill(3)))
    return response.json()


def get_item(path, row, item_href):
    response = requests.get(
        "{}/{}/{}/{}".format(base_path, str(path).zfill(3), str(row).zfill(3), item_href))
    return response.json()


def get_mtl(mtl_href):
    response = requests.get(mtl_href)

    return {
        "reflectance_mult": [float(val) for val in re.findall('REFLECTANCE_MULT_BAND_\d+\s+=\s+(.*)\n', response.text)],
        "reflectance_add": [float(val) for val in re.findall('REFLECTANCE_ADD_BAND_\d+\s+=\s+(.*)\n', response.text)],
        "sun_elevation": float(re.findall('SUN_ELEVATION\s+=\s+(.*)\n', response.text)[0])
    }


def get_masked_image(image_href, mask_polygon):
    data = rasterio.open(image_href)
    masked, mask_transform = mask(dataset=data, shapes=mask_polygon.geometry.to_crs(
        crs=data.crs.data), crop=True, all_touched=True)
    return masked[0, :, :], mask_transform


def sum_up(item, target_polygon, bands=[1, 2, 3, 4, 5, 6, 7, 9], max_len=None, nodata=0):
    mtl = get_mtl(item["assets"]["MTL"]["href"])
    ret = []

    for band in bands:
        href = item["assets"]["B{}".format(band)]["href"]
        masked, _ = get_masked_image(href, target_polygon)
        mult = mtl["reflectance_mult"][band - 1]
        add = mtl["reflectance_add"][band - 1]
        denominator = math.sin(math.radians(mtl["sun_elevation"]))
        values = masked.flatten()
        values = values[values != 0]
        if not max_len is None:
            values = values[:max_len]
        ret.append(list((values * mult + add) / denominator))
    return ret
