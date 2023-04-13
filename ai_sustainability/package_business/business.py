"""
This file contained all function used by the business part of our application
"""

import heapq

import numpy as np

from ai_sustainability.utils.models import AnswersList


class Business:
    """
    Class used by the application layer to make all the business thing of the app

    Methods :
        - calcul_best_ais: find the nb_ai best ai form all answers and the list of all AIs
    """

    def __init__(self) -> None:
        pass

    def calcul_best_ais(self, nb_ai: int, list_ai: list[str], list_answers: AnswersList) -> list[str]:
        coef_ai = np.array([1.0] * len(list_ai))
        for proposition_list in list_answers:
            for proposition in proposition_list:
                if proposition.list_coef:
                    coef_ai = np.multiply(coef_ai, np.array(proposition.list_coef))
        # we put all NaN value to -1
        for i_coef, coef in enumerate(coef_ai):
            if coef != coef:  # Abracadabra! ^^
                coef_ai[i_coef] = -1
        best = list(heapq.nlargest(nb_ai, np.array(coef_ai)))  # We sort and find the nb_ai best AIs
        # we put the best nb_ai in list_bests_ais
        list_bests_ais = []
        for i_ai in range(nb_ai):
            if best[i_ai] > 0:
                index = list(coef_ai).index(best[i_ai])
                list_bests_ais.append(list_ai[index])
        return list_bests_ais
