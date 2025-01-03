import logging
import re
import uuid

from lang_examples_common.utils.display_utils import display_foldable

log = logging.getLogger("langfuse-tutorial")

STRING_TO_LEVEL = dict(
    debug=logging.DEBUG,
    info=logging.INFO,
    warning=logging.WARNING,
    error=logging.ERROR,
    critical=logging.CRITICAL,
)


def log_and_add_to_report_critical(msg, class_name="p"):
    log_and_add_to_report(msg, "critical", class_name=class_name)


def log_and_add_to_report_info(msg, class_name="p"):
    log_and_add_to_report(msg, "info", class_name=class_name)


def log_and_add_to_report_debug(msg, class_name="p"):
    log_and_add_to_report(msg, "debug", class_name=class_name)


def log_and_add_to_report(msg, level, class_name="p"):
    level_value = STRING_TO_LEVEL[level]
    log.log(level_value, msg)

    html = f"<{class_name}>{msg}</{class_name}>"
    html = re.sub(
        "`(.*?)`", r"<code>\1</code>", html
    )  # add code blocks to the html report
    with open("report.html", "a") as f:
        f.write(html)
        f.write("\n")


def start_collapsible_section(show_open: bool = False):
    with open("report.html", "a") as f:
        f.write("<details open>" if show_open else "<details>")
        f.write("<summary>Click to expand/collapse</summary>\n")
        f.write("\n")


def end_collapsible_section():
    with open("report.html", "a") as f:
        f.write("</details>\n")
        f.write("\n")


def add_html_to_report(html):
    with open("report.html", "a") as f:
        html = re.sub(
            "`(.*?)`", r"<code>\1</code>", html
        )  # add code blocks to the html report
        f.write(html)
        f.write("\n")


def display_foldable_and_add_to_report(*args, **kwargs):
    html = display_foldable(*args, **kwargs)
    add_html_to_report(html)


def clean_report():
    with open("report.html", "w") as f:
        f.write(START_REPORT_HTML)


def close_report():
    with open("report.html", "a") as f:
        f.write(END_REPORT_HTML)


START_REPORT_HTML = """
<html><body>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        p {
            width: 50%;
            margin-top: 0;
        }
        table {
            width: "auto";
            border-collapse: collapse;
            font-size: 18px;
            text-align: left;
        }
        th, td {
            margin-left: 0px;
            padding: 0 6px 0 6px;
            border: 1px solid #ddd;
        }
        td {
          max-width: 400px;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #c2b5b5;
        }
        summary {
            margin: 10px 0 10px 0;
        }
        /* This is used when showing a dropdown that can select what table to show. Hide all tables initially. Then, we'll default to show the first table when loading the page */
        .multi-table-container {
            display: none;
            margin: 10px;
        }
        code {
            background-color: #f2f2f2;
            font-family: 'Courier New';
            font-size: 90%;
        }
    </style>
</head>
"""


END_REPORT_HTML = """
<script>
    function updateTables(selector, classname) {
        // Used to show/hide tables based on the selected value in the dropdown

        // Hide all tables initially
        const tables = document.getElementsByClassName(classname);
        for (let i = 0; i < tables.length; i++) {
            tables[i].style.display = 'none';
        }

        // Get selected value from the dropdown
        const selectedValue1 = document.getElementById(selector).value;
        console.log(selectedValue1);

        // Show the selected table
        if (selectedValue1) {
            document.getElementById(selectedValue1).style.display = 'block';
        }
    }
</script>
</body></html>
"""


def create_foldable_with_multi_table(
    tables, expand_name, dropdown_label="Select Table"
):
    """
    Display foldable with multiple tables
    """

    # generate a random uid
    uid = str(uuid.uuid4())

    html = f"""
    <details>
        <summary>{expand_name}</summary>
    """
    html += create_multi_table_html(uid, tables, dropdown_label)
    html += "\n</details>\n"
    return html


def create_multi_table_html(
    uid, tables: dict[str, str], dropdown_label="Select Table"
) -> str:
    """
    Create html for multiple tables with a dropdown to select which table to show
    """

    # generate a random uid
    uid = str(uuid.uuid4())
    html = '<div style="margin: 20">\n'
    html += f'<label for="tableSelect-{uid}">{dropdown_label}</label>\n'
    html += f"<select id=\"tableSelect-{uid}\" onchange=\"updateTables('tableSelect-{uid}', '{uid}')\">\n"
    for idx, table_name in enumerate(tables):
        selected = " selected" if idx == 0 else ""
        html += f'<option value="table-container-{uid}-{idx}"{selected}>{table_name}</option>\n'
    html += "</select>\n"
    html += "</div>\n"

    for idx, table_html in enumerate(tables.values()):
        html += f'<div id="table-container-{uid}-{idx}" class="{uid} multi-table-container">\n'
        html += table_html + "\n"
        html += "</div>\n"

    html += f"""
    <script>
        // Show Table 0 by default when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById("table-container-{uid}-0").style.display = 'block';
        }});
    </script>
    """

    return html
