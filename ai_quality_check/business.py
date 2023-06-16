"""File used for the business layer of the result displayer"""


from typing import Tuple

TABLE_LIST = ["Deployment", "Documentation", "Performance", "Model_Selection", "Pipeline", "Dataset"]


class Business:
    """Class used for all business task of the result displayer"""

    def __init__(self) -> None:
        pass

    def compute_score_one_page(self, data_page: dict) -> Tuple[int, int]:
        score = 0
        max_score = 0
        for cluster in data_page:
            if len(data_page[cluster]) == 1:
                max_score += 1
                if data_page[cluster][0].checked:
                    score += 1
            else:
                max_score += len(data_page[cluster])
                for check_elmt in data_page[cluster]:
                    if check_elmt.checked:
                        score += 1
        return score, max_score

    def compute_score(self, data: dict) -> dict[str, Tuple[int, int]]:
        result_dict: dict[str, Tuple[int, int]] = {}  # Dict with {page_name: (score, max_score)}
        for table_name in TABLE_LIST:
            result_dict[table_name] = self.compute_score_one_page(data[table_name])
        return result_dict
