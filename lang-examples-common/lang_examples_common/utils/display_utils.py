from string import Template
from typing import Callable, Iterable

import pandas as pd
from IPython.display import display_html
from pandas.io.formats.style import Styler

TEMPLATE_DISPLAY_FOLDABLE = Template(
    "<details$show_open><summary>$display_name</summary>$display_df</details>"
)


def display_foldable(
    data: pd.DataFrame | Iterable,
    name: str,
    show_open: bool = False,
    show_index: bool = False,
    col_space=None,
    float_format: Callable | None = None,
    show: bool = True,
    render_nested: bool = False,
    max_level_tables=1,
    max_level_expanders=None,
) -> str | None:
    """
    Display `data` with a button with the text `name` to fold/unfold
    Usually `data` is a pd.DataFrame or a pd.Series. In such a case,
    see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_html.html
    for possible values of `col_space` and how the different options work.

    We also support any iterable if `render_nested` is True
    In such a case, please adjust `max_level_tables` and `max_level_expanders` to your needs
    """
    if not render_nested:
        if isinstance(data, pd.Series):
            data = data.to_frame()
            show_index = True
        assert isinstance(
            data, (pd.DataFrame, pd.Series, Styler)
        ), "Only pd.DataFrame or pd.Series can be used if render_nested is False"
        html = data.to_html(
            col_space=col_space,
            index=show_index,
            float_format=float_format,
        )
    else:
        assert not isinstance(
            data, pd.DataFrame
        ), "`render_nested=True` does not support pd.DataFrame"
        html = table_renderer(
            data,
            show_open,
            max_level_tables=max_level_tables,
            max_level_expanders=max_level_expanders,
        )

    show_open = " open" if show_open else ""  # type: ignore
    html = TEMPLATE_DISPLAY_FOLDABLE.substitute(
        show_open=show_open,
        display_name=name,
        display_df=html,
    )
    if show:
        display_html(html, raw=True)

    return html


def table_renderer(data, show_open, level=0, max_level_tables=1, max_level_expanders=None):
    """
    Formats data as a table, potentially with expanders. When the value is simply str, float, int
    it just shows the value. But When being (dict, list, set, tuple), it might be formatted as a
    table with expanders
    """
    if isinstance(data, (str, float, int)) or max_level_tables is None or level > max_level_tables:
        return f"{data}"
    if max_level_expanders is not None and level > max_level_expanders:
        s = f"<details{show_open}><table>"
    else:
        s = "<table><tbody>"
    formatter_kwargs = dict(
        level=level + 1,
        max_level_tables=max_level_tables,
        max_level_expanders=max_level_expanders,
        show_open=show_open,
    )
    if isinstance(data, (dict, pd.Series)):
        for key, value in data.items():
            s += f"<tr><th>{key}</th><td>{table_renderer(value, **formatter_kwargs)}</td></tr>"
    elif isinstance(data, (list, set, tuple)):
        for item in data:
            s += f"<tr><td>{table_renderer(item, **formatter_kwargs)}</td></tr>"
    else:
        # raise NotImplementedError(str(type(data)))
        s+= str(data)
    if max_level_expanders is not None and level > max_level_expanders:
        return s + "</tbody></table></details>"
    else:
        return s + "</tbody></table>"
