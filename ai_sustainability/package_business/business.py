"""
This file contained all function used by the business part of our application

THIS FILE IS USELESS NOW
"""

import heapq
import math

import numpy as np

from ai_sustainability.package_business.models import AnswersList, Form


class Business:
    """
    Class used by the application layer to make all the business thing of the app

    Methods :
        - calcul_best_ais: find the nb_ai best ai form all answers and the list of all AIs
    """

    def __init__(self) -> None:
        pass

    def calcul_best_ais_old(
        self, nb_ai: int, list_ai: list[str], form_answers: list[AnswersList]
    ) -> list[str]:  # TODO suppr
        raw_coef_ai = np.array([1.0] * len(list_ai))
        for answer_list in form_answers:
            for answer in answer_list:
                if answer.list_coef:
                    raw_coef_ai = np.multiply(raw_coef_ai, np.array(answer.list_coef))
        # we put all NaN value to -1
        coef_ai = [-1 if math.isnan(coef) else coef for coef in raw_coef_ai]
        best_coefs = self.get_best_coefs(nb_ai, coef_ai)
        # we put the best nb_ai in list_bests_ais
        list_bests_ais = []
        for i_ai in range(nb_ai):
            if best_coefs[i_ai] > 0:
                index = list(coef_ai).index(best_coefs[i_ai])
                list_bests_ais.append(list_ai[index])
        return list_bests_ais

    def get_best_coefs(self, count: int, coefs: list[float]) -> list[float]:
        return list(heapq.nlargest(count, np.array(coefs)))  # We sort and find the nb_ai best AIs

    def calcul_best_ais(self, nb_ai: int, list_ai: list[str], form: Form) -> list[str]:  # TODO put this in Form
        raw_coef_ai = np.array([1.0] * len(list_ai))
        for question in form.question_list:
            for answer in question.answers_choosen:
                if answer.list_coef:
                    raw_coef_ai = np.multiply(raw_coef_ai, np.array(answer.list_coef))
        # we put all NaN value to -1
        coef_ai = [-1 if math.isnan(coef) else coef for coef in raw_coef_ai]
        list_bests_ais = []
        for index, ai_name in enumerate(list_ai):
            list_bests_ais.append((ai_name, coef_ai[index]))
        list_bests_ais.sort(key=lambda x: x[1], reverse=True)
        return []
        return [x[0] for x in list_bests_ais][:nb_ai]
