from typing import Dict, NamedTuple, Tuple


class ScrapedData(NamedTuple):
    page_number_: int
    page_url_: str
    group_id_: int
    group_index_: int
    element_index_: int
    # actual collected data
    data: Dict


def scraped_data_sorter(data: ScrapedData) -> Tuple[int, int, int, int]:
    return data.page_number_, data.group_index_, data.group_id_, data.element_index_


def scraped_data_grouper(data: ScrapedData) -> Tuple[int, str, int, int, int]:
    return data.page_number_, data.page_url_, data.group_index_, data.group_id_, data.element_index_
