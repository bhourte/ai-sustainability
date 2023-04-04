"""
Class which contains the form composed of the different questions/answers
Streamlit class

methods:
    - display_question
    - display_answer
    - ...

    ONE QUESTION :
    return : dict {
            1: question_text
            2: answers
            3: help_text
            4: question_label
        }
    
    A chaque réponse de l'utilisateur, retourner le texte de celle-ci ainsi que les anciennes réponses (list(str))
    Pour Q_QRM, list dans list (list(list(str)))
    Pour Q_NEXT, Q_QCM, str answer    
"""
