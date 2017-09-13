import csv
import json
from rtree import index
SCENE_LIST = 'scene_list'

def main():

    print 'Loading spatial index'
    scene_index = index.Index(interleaved=False)
    with open(SCENE_LIST) as scenes:
        reader = csv.DictReader(scenes)
        for row_num, row in enumerate(reader):
            bbox = tuple(float(row[attr]) for attr in ('min_lat', 'max_lat', 'min_lon', 'max_lon'))
            data = dict((key, row[key]) for key in ('productId', 'cloudCover', 'path', 'row', 'download_url'))
            scene_index.insert(row_num, bbox, obj=json.dumps(data))
    print 'Done.'

    intersecting_bbox = (68.40073, 75.74251, 24.4185, 35.93353)
    for matching_raster in scene_index.intersection(intersecting_bbox, objects=True):
        data = json.loads(matching_raster.object)
        for band_num in (1, 2, 6):
            filename = "{product_id}_B{band}.TIF".format(
                product_id=data['productId'],
                band=band_num)
            print data['download_url'].replace('index.html', filename)

if __name__ == '__main__':
    main()

# Need an argparse UI to:
#   * Select bands
#   * Filter by cloud cover
#   * define lat/long bbox
#   * define allowed processing collection levels (precision terrain [L1TP], systematic terrain [L1GS], systematic [L1GS]
