
from pathlib import Path
import re
import requests
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.transform import array_bounds


# ---------------------------------------------------------
# WORLDCORE DAY 25
# Copernicus DEM download and processing
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw" / "dem"
PROCESSED_DIR = ROOT / "data" / "processed" / "terrain"
REPORT_DIR = ROOT / "reports" / "terrain"

for folder in [RAW_DIR, PROCESSED_DIR, REPORT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"
CATALOGUE_URL = f"{BASE_URL}/tileList.txt"

# Approximate working extent for Ernakulam.
# Replace with an authoritative district boundary for final work.
WEST = 76.0
SOUTH = 9.7
EAST = 76.7
NORTH = 10.3

# Copernicus DEM source tile resolution identifier:
# 10 arc-seconds = nominal GLO-30 product.
RESOLUTION_ID = "10"

TIMEOUT = 120


def get_required_tile_names(catalogue_text):

    pattern = re.compile(
        r"Copernicus_DSM_COG_10_"
        r"([NS])(\d{2})_00_"
        r"([EW])(\d{3})_00_DEM"
    )

    available = set()

    for match in pattern.finditer(catalogue_text):
        available.add(match.group(0))

    required = []

    min_lat = int(np.floor(SOUTH))
    max_lat = int(np.floor(NORTH))
    min_lon = int(np.floor(WEST))
    max_lon = int(np.floor(EAST))

    for lat in range(min_lat, max_lat + 1):
        for lon in range(min_lon, max_lon + 1):

            lat_prefix = "N" if lat >= 0 else "S"
            lon_prefix = "E" if lon >= 0 else "W"

            tile_name = (
                f"Copernicus_DSM_COG_{RESOLUTION_ID}_"
                f"{lat_prefix}{abs(lat):02d}_00_"
                f"{lon_prefix}{abs(lon):03d}_00_DEM"
            )

            if tile_name in available:
                required.append(tile_name)
            else:
                print(f"Catalogue does not list: {tile_name}")

    return required


def download_tile(tile_name):

    filename = f"{tile_name}.tif"
    destination = RAW_DIR / filename

    if destination.exists() and destination.stat().st_size > 100_000:
        print(f"Already downloaded: {filename}")
        return destination

    url = f"{BASE_URL}/{tile_name}/{filename}"

    print(f"\nDownloading: {tile_name}")

    response = requests.get(
        url,
        stream=True,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    temp_path = destination.with_suffix(".download")

    with open(temp_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    if temp_path.stat().st_size < 100_000:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Downloaded file is unexpectedly small: {tile_name}"
        )

    temp_path.replace(destination)

    print(f"Saved: {destination}")

    return destination


def main():

    print("WORLDCORE — Copernicus DEM processing")
    print("Study extent:", WEST, SOUTH, EAST, NORTH)

    print("\n1. Reading public tile catalogue...")

    response = requests.get(
        CATALOGUE_URL,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    tile_names = get_required_tile_names(response.text)

    if not tile_names:
        raise RuntimeError(
            "No required GLO-30 tiles were found in the public catalogue. "
            "Check tile coverage or use the GLO-90 fallback."
        )

    print("\nAvailable required tiles:")
    for name in tile_names:
        print(" -", name)

    print("\n2. Downloading tiles...")

    tile_paths = [
        download_tile(name)
        for name in tile_names
    ]

    print("\n3. Validating raster tiles...")

    sources = []

    for path in tile_paths:
        dataset = rasterio.open(path)

        print("\nFile:", path.name)
        print("CRS:", dataset.crs)
        print("Bounds:", dataset.bounds)
        print("Resolution:", dataset.res)
        print("NoData:", dataset.nodata)
        print("Dimensions:", dataset.width, dataset.height)

        if dataset.crs is None:
            raise ValueError(f"Missing CRS: {path.name}")

        sources.append(dataset)

    print("\n4. Merging tiles...")

    mosaic, mosaic_transform = merge(sources)

    profile = sources[0].profile.copy()

    for source in sources:
        source.close()

    profile.update(
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        transform=mosaic_transform,
        count=1,
        compress="lzw"
    )

    mosaic_path = PROCESSED_DIR / "worldcore_dem_mosaic.tif"

    with rasterio.open(mosaic_path, "w", **profile) as dst:
        dst.write(mosaic[0], 1)

    print("Saved mosaic:", mosaic_path)

    print("\n5. Clipping to working study extent...")

    clip_polygon = [{
        "type": "Polygon",
        "coordinates": [[
            [WEST, SOUTH],
            [EAST, SOUTH],
            [EAST, NORTH],
            [WEST, NORTH],
            [WEST, SOUTH]
        ]]
    }]

    with rasterio.open(mosaic_path) as src:

        if src.crs.to_epsg() != 4326:
            raise ValueError(
                "Expected geographic EPSG:4326 source data. "
                "Inspect the source CRS before changing this workflow."
            )

        clipped, clipped_transform = mask(
            src,
            clip_polygon,
            crop=True,
            nodata=src.nodata if src.nodata is not None else -9999
        )

        clipped_profile = src.profile.copy()
        clipped_profile.update(
            height=clipped.shape[1],
            width=clipped.shape[2],
            transform=clipped_transform,
            nodata=src.nodata if src.nodata is not None else -9999,
            compress="lzw"
        )

    clipped_path = PROCESSED_DIR / "worldcore_dem_ernakulam_clip.tif"

    with rasterio.open(clipped_path, "w", **clipped_profile) as dst:
        dst.write(clipped)

    print("Saved clipped DEM:", clipped_path)

    print("\n6. Reprojecting to UTM Zone 43N for terrain calculations...")

    with rasterio.open(clipped_path) as src:

        target_crs = "EPSG:32643"

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds,
            resolution=30
        )

        destination = np.full(
            (height, width),
            -9999,
            dtype=np.float32
        )

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=transform,
            dst_crs=target_crs,
            dst_nodata=-9999,
            resampling=Resampling.bilinear
        )

        projected_profile = src.profile.copy()
        projected_profile.update(
            crs=target_crs,
            transform=transform,
            width=width,
            height=height,
            dtype="float32",
            nodata=-9999,
            compress="lzw"
        )

    projected_path = PROCESSED_DIR / "worldcore_dem_utm43n.tif"

    with rasterio.open(projected_path, "w", **projected_profile) as dst:
        dst.write(destination, 1)

    print("Saved projected DEM:", projected_path)

    print("\n7. Generating elevation statistics...")

    valid = destination[
        np.isfinite(destination) &
        (destination != -9999)
    ]

    if valid.size == 0:
        raise RuntimeError("No valid elevation pixels found.")

    stats = {
        "pixel_count": int(valid.size),
        "minimum_elevation_m": float(np.min(valid)),
        "maximum_elevation_m": float(np.max(valid)),
        "mean_elevation_m": float(np.mean(valid)),
        "median_elevation_m": float(np.median(valid)),
        "std_elevation_m": float(np.std(valid)),
        "crs": "EPSG:32643",
        "working_extent": f"{WEST},{SOUTH},{EAST},{NORTH}",
        "source": "Copernicus DEM GLO-30 Public",
        "data_type": "Digital Surface Model"
    }

    import pandas as pd

    stats_path = REPORT_DIR / "worldcore_dem_statistics.csv"

    pd.DataFrame([stats]).to_csv(
        stats_path,
        index=False
    )

    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nStatistics saved:", stats_path)

    print("\nWORLDCORE DEM processing completed.")


if __name__ == "__main__":
    main()
