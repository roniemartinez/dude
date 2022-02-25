from typing import Dict, NamedTuple, Tuple


class ScrapedData(NamedTuple):
    page_number: int
    page_url: str
    group_id: int
    group_index: int
    element_index: int
    # actual collected data
    data: Dict


def scraped_data_sorter(data: ScrapedData) -> Tuple[int, int, int, int]:
    return data.page_number, data.group_index, data.group_id, data.element_index


def scraped_data_grouper(data: ScrapedData) -> Tuple[int, str, int, int, int]:
    return data.page_number, data.page_url, data.group_index, data.group_id, data.element_index
