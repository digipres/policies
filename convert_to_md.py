"""Convert to Markdown.

Data is extracted from Google Sheets exported as a CSV and stored in the
script below as a string for processing.
"""

import csv
import io
from typing import Final, Tuple

# Index of COUNTRY column in CSV, used, for example, for sorting, below.
COUNTRY_INDEX: Final[str] = 2


def format_front_matter(front_matter: str) -> str:
    """Improve the look of the front matter for publishing.

    This is all quite rudimentary. Ideal would be to format the source
    better.
    """

    header: Final[str] = "Digital preservation policies and strategies"
    attribution: Final[str] = "CREATED BY:"
    created: Final[str] = "DATE CREATED:"
    history: Final[str] = "VERSION HISTORY:"
    history_no_colon: Final[str] = "## VERSION HISTORY"

    front_matter = front_matter.replace(front_matter, f"# {header}\n{front_matter}\n")
    front_matter = front_matter.replace(attribution, f"\n**{attribution}**")
    front_matter = front_matter.replace(created, f"\n**{created}**")
    front_matter = front_matter.replace(history, f"\n{history_no_colon}")

    front_matter = f"{front_matter}\n## Listing\n"

    return front_matter


def parse_csv(csv_name) -> (str, str):
    """Take the contents of the given CSV and return it as two
    components.

    Return the metadata which appears at the top, and then the CSV data
    format itself.
    """
    csv_data = ""
    front_matter = ""

    with open(csv_name, encoding="utf8") as csv_file:
        contents = csv_file.read()

        csv_idx = contents.find(
            ",NAME OF INSTITUTION,COUNTRY ,POLICY ,POLICY URL,STRATEGY ,STRATEGY URL"
        )
        csv_data = contents[csv_idx:]

        front_matter = contents[0:csv_idx]
        front_matter = front_matter.replace('",,,,,,', "").strip()[1:]

    if not csv_data.startswith("ORDER"):
        csv_data = f"ORDER{csv_data}"

    front_matter = format_front_matter(front_matter)
    return front_matter, csv_data


def map_fields(data: str) -> list[list[Tuple[str, str]]]:
    """Map fields for convenience into a new list with field names
    associated with the corresponding data.
    """
    csvfile = io.StringIO(data)
    sheet = csv.reader(csvfile, delimiter=",", quotechar='"')
    header = None
    mapped = []
    for idx, item in enumerate(sheet):
        if idx == 0:
            header = [formatted_item.strip() for formatted_item in item]
            continue
        formatted = [formatted_item.strip() for formatted_item in item]
        mapped.append(list(zip(header, formatted)))
    return mapped


def _sort_list(list_: list, index=COUNTRY_INDEX) -> list[list[Tuple[str, str]]]:
    """Sort list given an index value."""
    list_.sort(key=lambda item: item[index])
    return list_


def _capitalize(text: str) -> str:
    """Capitalize the first letter of a value unless it requires an
    exception.
    """
    if text.lower() in ("usa",):
        return text.upper()
    return text.capitalize()


def _title(text: str) -> str:
    """Title case a value, i.e. make the first character of a sentence
    upper case, unless it requires an exception.
    """
    text = text.title()
    # NB. space, so as not to match countries like Ukraine.
    if "Uk " in text:
        text = text.replace("Uk ", "UK ")
    if "Usa " in text:
        text = text.replace("Usa ", "USA ")
    return text


def format_entry(item: list) -> str:
    """Format an entry as a string for output in Markdown."""
    unavailable: Final[str] = "Not available"
    inst = _title(value(item[1]))
    policy_url = unavailable if not value(item[4]) else value(item[4])
    strat_url = unavailable if not value(item[6]) else value(item[6])
    if policy_url != unavailable:
        policy_url = f"[{policy_url}]({policy_url})"
    if strat_url != unavailable:
        strat_url = f"[{strat_url}]({strat_url})"
    metadata = f"### {inst}\n* **Policy**: {policy_url}\n* **Strategy**: {strat_url}\n"
    return metadata


def value(keypair):
    """Return the value from a key,pair tuple."""
    return keypair[1].strip()


def add_md(metadata: str, more_metadata: str) -> str:
    """Add markdown to markdown and add a newline."""
    return f"{metadata}{more_metadata}\n"


def data_to_markdown(entries: list[list[Tuple[str, str]]]) -> str:
    """Convert our data to markdown.
    An entry looks as follows:
    [
        ('ORDER', 'N'),
        ('NAME OF INSTITUTION', 'NATIONAL ARCHIVES OF AUSTRALIA'),
        ('COUNTRY ', 'AUSTRALIA '),
        ('POLICY ', ''),
        ('POLICY URL', 'https://example.com'),
        ('STRATEGY ', ''),
        ('STRATEGY URL', '')
    ]
    """
    entries = _sort_list(entries)
    metadata = ""
    country = None
    for item in entries:
        if item[COUNTRY_INDEX] != country:
            country = item[COUNTRY_INDEX]
            metadata = f"{metadata}## {_capitalize(value(country))}\n"
        more_metadata = format_entry(item)
        metadata = add_md(metadata, more_metadata)
    return metadata


def make_toc(metadata: str) -> str:
    """Make a table of contents for the markdown generated by this
    utility.
    """
    toc = ""
    for line in metadata.split("\n"):
        # Exceptions 80/20:
        if "(Note: Dp Policy Framework)" in line:
            line = line.replace("(Note: Dp Policy Framework)", "").strip()
        # Regular path of execution.
        if line.startswith("###"):
            title = line.replace("### ", "")
            line = line.lower().replace("### ", "").replace(" ", "-")
            line = f"  * [{title}](#{line})"
            toc = f"{toc}\n{line}"
            continue
        if line.startswith("##"):
            title = line.replace("## ", "")
            line = line.lower().replace("## ", "").replace(" ", "-")
            line = f"- [{title}](#{line})"
            toc = f"{toc}\n{line}"
            continue
    return toc


def make_doc(front_matter: str, metadata: str) -> str:
    """Create a complete markdown document from our data."""
    toc = make_toc(metadata)
    return f"{front_matter}{toc}\n\n{metadata}".strip()


def main(csv_name: str) -> None:
    """Primary entry point for this script."""
    front_matter, data = parse_csv(csv_name)
    entries = map_fields(data)
    metadata = data_to_markdown(entries)
    doc = make_doc(front_matter, metadata)
    return doc


if __name__ == "__main__":
    main("")
