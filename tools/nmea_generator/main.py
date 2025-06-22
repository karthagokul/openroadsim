#
# MIT License
# Copyright (c) 2024 Gokul Kartha <kartha.gokul@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString
from geopy.distance import geodesic
import pynmea2
from datetime import datetime, timedelta
import argparse

def to_nmea(val, is_lat):
    deg = int(abs(val))
    minutes = (abs(val) - deg) * 60
    formatted = f"{deg:02d}{minutes:06.3f}"
    direction = ("N" if val >= 0 else "S") if is_lat else ("E" if val >= 0 else "W")
    return formatted, direction

def generate_nmea_from_shapefile(shapefile_path, start_coord, end_coord, output_path, max_distance=None):
    print("Reading the Shapefile " + shapefile_path)
    roads = gpd.read_file(shapefile_path).to_crs(epsg=4326)
    print("Generating Graph")
    # Build graph from road LineStrings
    G = nx.Graph()
    for _, row in roads.iterrows():
        geom = row.geometry
        if isinstance(geom, LineString):
            coords = list(geom.coords)
            for i in range(len(coords) - 1):
                pt1, pt2 = coords[i], coords[i + 1]
                dist = geodesic((pt1[1], pt1[0]), (pt2[1], pt2[0])).meters
                G.add_edge(pt1, pt2, weight=dist)

    # Snap to nearest graph nodes
    start_node = min(G.nodes, key=lambda x: geodesic((x[1], x[0]), start_coord).meters)
    end_node = min(G.nodes, key=lambda x: geodesic((x[1], x[0]), end_coord).meters)

    print("Got the Start and End Node , Now Computing the Path")
    # Compute path
    path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')

    # Trim path to max_distance (if given)
    if max_distance:
        trimmed_path = [path[0]]
        total_dist = 0
        for i in range(1, len(path)):
            d = geodesic((path[i-1][1], path[i-1][0]), (path[i][1], path[i][0])).meters
            if total_dist + d > max_distance:
                break
            trimmed_path.append(path[i])
            total_dist += d
        path = trimmed_path

    # Generate NMEA sentences
    start_time = datetime.utcnow()
    nmea_lines = []

    for i, (lon, lat) in enumerate(path):
        timestamp = (start_time + timedelta(seconds=i)).strftime("%H%M%S")
        date = start_time.strftime("%d%m%y")
        nmea_lat, lat_dir = to_nmea(lat, True)
        nmea_lon, lon_dir = to_nmea(lon, False)

        rmc = pynmea2.RMC('GP', 'RMC', (
            timestamp, 'A', nmea_lat, lat_dir, nmea_lon, lon_dir,
            '065.5', '123.4', date, '', '', 'A'
        ))
        nmea_lines.append(str(rmc))

    with open(output_path, "w") as f:
        f.write("\n".join(nmea_lines))

    print(f"✅ NMEA file written to {output_path} with {len(nmea_lines)} points.")

def main():
    parser = argparse.ArgumentParser(description="Generate NMEA GPS trace from a road shapefile.")
    parser.add_argument("--shapefile", required=True, help="Path to roads shapefile (e.g. roads.shp)")
    parser.add_argument("--start-lat", type=float, required=True, help="Start latitude")
    parser.add_argument("--start-lon", type=float, required=True, help="Start longitude")
    parser.add_argument("--end-lat", type=float, required=True, help="End latitude")
    parser.add_argument("--end-lon", type=float, required=True, help="End longitude")
    parser.add_argument("--output", required=True, help="Output NMEA file path")
    parser.add_argument("--max-distance", type=float, default=None, help="Optional max distance in meters")

    args = parser.parse_args()
    print("Go and get a coffee, depending on the size of the shapefile, it take some time :)")

    generate_nmea_from_shapefile(
        shapefile_path=args.shapefile,
        start_coord=(args.start_lat, args.start_lon),
        end_coord=(args.end_lat, args.end_lon),
        output_path=args.output,
        max_distance=args.max_distance
    )

if __name__ == "__main__":
    main()
