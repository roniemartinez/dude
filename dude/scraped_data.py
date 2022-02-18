from typing import Dict, NamedTuple


class ScrapedData(NamedTuple):
    page_number: int
    page_url: str
    group_id: int
    group_index: int
    element_index: int
    data: Dict


def scraped_data_sorter(data: ScrapedData):
    return data.page_number, data.group_index, data.group_id, data.element_index


def scraped_data_grouper(data: ScrapedData):
    return data.page_number, data.page_url, data.group_index, data.group_id, data.element_index
