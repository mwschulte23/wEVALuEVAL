# import requests
# import instructor
# import Levenshtein
# import anthropic
import yaml

from datetime import datetime
from instructor.batch import BatchJob
from typing import Any, Callable, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

from scorer_pipe import Scorer
from eval_wrapper import Eval


class Score(BaseModel):
    score: int = Field(..., description='Provide a score for user wellbeing. Must be greater than 0, less than 100.')
    reasoning: str = Field(..., max_length=280, description='Provide concise reasoning for the chosen score. Must be fewer than 140 characters')
    suggestion: str = Field(..., max_length=280, description='Suggestions for the user to a improve low to mid score or persist a high score.')
    # connectedness: int = Field(..., le=0, ge=100, description='Provide a score for user connectedness.')
    # happiness: int = Field(..., le=0, ge=100, description='Provide a score for user happiness.')


def get_user_score(x, **kwargs):
    print(x)
    user_input = int(input('Input 1 for good response, 0 for bad: '))
    while user_input not in [0, 1]:
        print('Invalid input. Must be either 0 (bad) or 1 (good).')
        user_input = int(input('Input 1 for good response, 0 for bad: '))
    return user_input



if __name__ == '__main__':
    scorer = Scorer(Score)
    scorer.add_score('user_score', get_user_score, 'score')
    scorer.add_score('user_score', get_user_score, 'reasoning')
    scorer.add_score('user_score', get_user_score, 'suggestion')
    queries = [
        '''
            Today was up and down. I had to fix a poor implementation of my work caused by a massive communication breakdown. But have two co-workers that I can talk with about it.
            After work was great. My wfie was happy, kid was in good spirits and we were able to hang outside.
        ''',
        '''
            Recently, I've been pretty balanced. Love being a parent 90% of the time, live comfortably but aspire for more, and am slowly pursuing new opportunities. All in all life is good, job is rough, and am generally grateful.
        '''
        # '''
        #     Today was fantastic! I nailed my work presentation, and the team's energy was infectious. Even when faced with a last-minute crisis, I stayed calm and found a creative solution.
        #     Had a great lunch with Sarah, deepening our friendship. Ended the day with a joyful family dinner, feeling grateful for Mom's improved health. I'm filled with contentment and ready for whatever life brings.
        # ''',
        # '''
        #     Work was uneventful today, and my back pain was manageable. Had coffee with John - nice to catch up, though our conversations rarely go deep.
        #     Bills are paid, and there's food in the fridge, which is something to be thankful for. I can't shake the feeling I should be doing more with my life, but I'll manage. I always do.
        # ''',
        # '''
        #     Another day of dread and pain. Work is a nightmare - I'm behind and unfocused, likely to lose this job too. I've been ignoring calls from Mom and have no energy for social connections.
        #     The pile of unpaid bills keeps growing, and I don't know how I'll make rent. I'm exhausted by feeling this way and seeing no way out. What's the point of it all?
        # '''
    ]
    eval = Eval(task_id=1, stack_id=4, response_model=Score, queries=queries, score_pipe=scorer)
    logs = eval.run()
    print(logs)
