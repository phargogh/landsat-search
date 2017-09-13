import time

import requests

# Timings:
# * Rtree with .insert for each record: ~29s.
# * Rtree with generator on init: ~9s
# * Filtering while reading in the CSV and just locating matching scenes: ~2.9s
# * Reducing iterators and generators (and line profiling): ~0.25s
#
# Speedup factor: 104x


SCENE_LIST = 'scene_list'


def combined():
    intersecting_bbox = (68.40073, 75.74251, 24.4185, 35.93353)
    src_min_lat, src_max_lat, src_min_lon, src_max_lon = intersecting_bbox
    start_time = time.time()
    found_ids = []

    total_download_size = 0.
    with open(SCENE_LIST) as scenes:
        scenes.readline()  # skip the header
        for row_num, line in enumerate(scenes):
            productId, entityId, acquisitionDate, cloudCover, processingLevel, path, row, min_lat, min_lon, max_lat, max_lon, download_url = line.strip().split(',')

            if float(min_lat) <= src_min_lat:
                continue
            if float(max_lat) >= src_max_lat:
                continue
            if float(min_lon) <= src_min_lon:
                continue
            if float(max_lon) >= src_max_lon:
                continue
            found_ids.append(productId)

            for band_num in (1, 2, 6):
                filename = "{product_id}_B{band}.TIF".format(
                    product_id=productId,
                    band=band_num)
                raster_url = download_url.replace('index.html', filename)
                filesize = int(requests.head(raster_url).headers['Content-Length']) / 1024**2.
                total_download_size += filesize
                print "%55s (%s MB)" % (filename, round(filesize, 2))

    print "Total download size: %s MB." % round(total_download_size, 2)
    print 'filter2 done. (%ss)' % round(time.time() - start_time, 2)

    return found_ids


if __name__ == '__main__':
    combined_results = combined()

# Need an argparse UI to:
#   * Download latest scene list
#   * Select bands
#   * Filter by cloud cover
#   * define lat/long bbox
#   * define allowed processing collection levels (precision terrain [L1TP], systematic terrain [L1GS], systematic [L1GS]
#   * limit the date range allowed
#   * Limit to the first n results.
#   * Use OGR or fiona to create a warped VRT of a provided AOI vector to
#       determine lat/long bbox.
