import logging
from typing import Dict, Optional, Union

import geopandas as gpd


def _validate_space_params(
    clip: str,
    geometry: Union[Dict[str, tuple], gpd.GeoDataFrame],
    averaging: bool = False,
    unique_id: Optional[str] = None,
):
    _clip_available_methods = ["bbox", "point", "polygon", None]

    if clip not in _clip_available_methods:
        raise ValueError(f"clip value '{clip}' is not one of {_clip_available_methods}")

    if not isinstance(averaging, bool):
        raise ValueError(f"averaging value '{averaging}' should be a boolean")

    if not (isinstance(unique_id, type(None)) or isinstance(unique_id, str)):
        raise ValueError(f"unique_id value '{unique_id}' should be a string")

    if unique_id is not None:
        if isinstance(geometry, gpd.GeoDataFrame) and unique_id not in geometry.columns:
            message = (
                f"\nunique_id value '{unique_id}' was not found in gpd.GeoDataFrame \n"
                f"so a random index will be used instead."
            )
            logging.warning(message)

    if averaging is True and not isinstance(geometry, gpd.GeoDataFrame):
        message = (
            f"\naveraging value '{averaging}' is not necessary \n"
            f"because geometry is not a GeoPandas GeoDataFrame.\n"
            f"averaging value will be ignored."
        )
        logging.warning(message)

    if averaging is True and clip in ["point"]:
        message = (
            f"\naveraging value '{averaging}' is not necessary \n"
            f"because clip operation requested is on a {clip}.\n"
            f"averaging value will be ignored."
        )
        logging.warning(message)

    if unique_id is not None and not isinstance(geometry, gpd.GeoDataFrame):
        message = (
            f"\nunique_id value '{unique_id}' is not necessary \n"
            f"because geometry is not a GeoPandas GeoDataFrame.\n"
            f"unique_id value will be ignored."
        )
        logging.warning(message)

    return True
