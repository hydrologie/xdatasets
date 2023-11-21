import uuid
from functools import reduce
from html import escape

from IPython.core.display import HTML
from xarray.core.formatting_html import _icon, _mapping_section, _obj_repr

catalog_path = "https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml"


def open_dataset(
    name: str,
    **kws,
):
    r"""Open a dataset from the online public repository (requires internet).

    Available datasets:
    * ``"era5_reanalysis_single_levels"``: ERA5 reanalysis subset (t2m and tp)
    * ``"cehq"``: CEHQ flow and water levels observations

    Parameters
    ----------
    name : str
        Name of the file containing the dataset.
        e.g. 'era5_reanalysis_single_levels'
    \*\*kws : dict, optional
        Passed to xarray.open_dataset

    See Also
    --------
    xarray.open_dataset
    """
    try:
        import intake
    except ImportError as e:
        raise ImportError(
            "tutorial.open_dataset depends on intake and intake-xarray to download and manage datasets."
            " To proceed please install intake and intake-xarray."
        ) from e

    cat = intake.open_catalog(catalog_path)
    dataset_info = [
        (category, dataset_name)
        for category in cat._entries.keys()
        for dataset_name in cat[category]._entries.keys()
        if dataset_name == name
    ]

    data = reduce(lambda array, index: array[index], dataset_info, cat)

    if data.describe()["driver"][0] == "geopandasfile":
        data = data.read()
    elif data.describe()["driver"][0] == "zarr":
        data = data.to_dask()
    else:
        raise NotImplementedError(
            f"Dataset {name} is not available. Please request further datasets to our github issues pages"
        )
    return data


def summarize_coords(variables):
    li_items = []
    for k in variables:
        li_content = summarize_variable(k, is_index=False)
        li_items.append(f"<li class='xr-var-item'>{li_content}</li>")

    vars_li = "".join(li_items)

    return f"<ul class='xr-var-list'>{vars_li}</ul>"


def summarize_variable(name, is_index=False, dtype=None):
    cssclass_idx = " class='xr-has-index'" if is_index else ""
    name = escape(str(name))

    # "unique" ids required to expand/collapse subsections
    attrs_id = "attrs-" + str(uuid.uuid4())
    data_id = "data-" + str(uuid.uuid4())
    attrs_icon = _icon("icon-file-text2")
    data_icon = _icon("icon-database")

    return (
        f"<div class='xr-var-preview'><span{cssclass_idx}>{name}</span></div>"
        f"<input id='{attrs_id}' class='xr-var-attrs-in' "
        f"type='checkbox'>"
        f"<label for='{attrs_id}' title='Show/Hide attributes'>"
        f"{attrs_icon}</label>"
        f"<input id='{data_id}' class='xr-var-data-in' type='checkbox'>"
        f"<label for='{data_id}' title='Show/Hide data repr'>"
        f"{data_icon}</label>"
    )


def list_available_datasets():
    """Open, load lazily, and close a dataset from the public online repository (requires internet).

    See Also
    --------
    open_dataset
    """
    try:
        import intake
    except ImportError as e:
        raise ImportError(
            "tutorial.open_dataset depends on intake and intake-xarray to download and manage datasets."
            " To proceed please install intake and intake-xarray."
        ) from e

    cat = intake.open_catalog(catalog_path)

    # This will need refactor if the catalog has more than 2 levels
    # list(itertools.chain.from_iterable([list(cat[name].keys()) for name in cat._entries.keys()]))

    datasets_catalog = {
        field: list(sorted(cat[field]._entries.keys()))
        for field in sorted(cat._entries.keys())
    }

    def add_section(datasets_catalog):
        return [
            _mapping_section(
                datasets,
                name=field.capitalize(),
                details_func=summarize_coords,
                max_items_collapse=25,
                expand_option_name="display_expand_coords",
            )
            for field, datasets in datasets_catalog.items()
        ]

    a = _obj_repr(
        "",
        [f"<div class='xr-obj-type'>{escape('xdatasets.Catalog')}</div>"],
        add_section(datasets_catalog),
    )

    return HTML(a)


def load_dataset(*args, **kwargs):
    """Open, load lazily, and close a dataset from the online repository (requires internet).

    See Also
    --------
    open_dataset
    """
    return open_dataset(*args, **kwargs)
