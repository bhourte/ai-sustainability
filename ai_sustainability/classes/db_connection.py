"""
Make the connection to the database, run the querys and close the connection

1)

    get_first_question() : get the first question of the form
    get_one_question() : 
        - get_question_text() : get the text of the question (str) with actual_question
        - get_answers_text() list of all the answers (str) with actual_question
        - get_help_text() : get the help text (str) with actual_question

        return : dict {
            1: text question
            2: list of answers
            3: help text
            4: Label question
        }
    save_answer() : save the answer in the database

    give answer(answer_list) : following the len of the list, we can find the question by the answer

    attributes :
        - list_questions (list) : list of past questions and last is actual_question (ids db)
    
        




"""
