"""File used for the business layer of the result displayer"""


from typing import Tuple

TABLE_LIST = ["Deployment", "Documentation", "Performance", "Model_Selection", "Pipeline", "Dataset"]


class Business:
    """Class used for all business task of the result displayer"""

    def __init__(self) -> None:
        pass

    def compute_score(self, data: dict) -> dict:
        result_dict: dict[str, Tuple[int, int]] = {}  # Dict with {page_name: (score, max_score)}
        for table_name in TABLE_LIST:
            score = 0
            max_score = 0
            for cluster in data[table_name]:
                if len(data[table_name][cluster]) == 1:
                    max_score += 1
                    if data[table_name][cluster][0].checked:
                        score += 1
                else:
                    max_score += len(data[table_name][cluster])
                    for check_elmt in data[table_name][cluster]:
                        if check_elmt.checked:
                            score += 1
            result_dict[table_name] = (score, max_score)
        return result_dict
