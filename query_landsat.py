import csv
import json
import time

from rtree import index
import requests

# 29s


SCENE_LIST = 'scene_list'

def main():

    print 'Loading spatial index'
    start_time = time.time()
    def _load_data():
        with open(SCENE_LIST) as scenes:
            reader = csv.DictReader(scenes)
            for row_num, row in enumerate(reader):
                bbox = tuple(float(row[attr]) for attr in ('min_lat', 'max_lat', 'min_lon', 'max_lon'))
                data = dict((key, row[key]) for key in ('productId', 'cloudCover', 'path', 'row', 'download_url'))
                yield (row_num, bbox, json.dumps(data))

    # Loading like so yields a 3x speedup.
    scene_index = index.Index(_load_data(), interleaved=False)

            #scene_index.insert(row_num, bbox, obj=json.dumps(data))
    print 'Done. (%ss)' % round(time.time() - start_time, 2)

    intersecting_bbox = (68.40073, 75.74251, 24.4185, 35.93353)
    total_download_size = 0.
    for matching_raster in scene_index.intersection(intersecting_bbox, objects=True):
        data = json.loads(matching_raster.object)
        for band_num in (1, 2, 6):
            filename = "{product_id}_B{band}.TIF".format(
                product_id=data['productId'],
                band=band_num)
            raster_url = data['download_url'].replace('index.html', filename)
            filesize = int(requests.head(raster_url).headers['Content-Length']) / 1024**2.
            total_download_size += filesize
            print "%55s (%s MB)" % (filename, round(filesize, 2))
    print "Total download size: %s MB." % round(total_download_size, 2)


if __name__ == '__main__':
    main()

# Need an argparse UI to:
#   * Download latest scene list
#   * Select bands
#   * Filter by cloud cover
#   * define lat/long bbox
#   * define allowed processing collection levels (precision terrain [L1TP], systematic terrain [L1GS], systematic [L1GS]
#   * limit the date range allowed
#   * Limit to the first n results.
