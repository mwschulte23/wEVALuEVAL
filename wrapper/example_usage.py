import requests
import instructor
import Levenshtein
import anthropic

from datetime import datetime
from instructor.batch import BatchJob
from typing import Any, Callable, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

from scorer_pipe import Scorer
from eval_wrapper import Eval


score_sys_msg_var = {
    'wellbeing': {
        'category': 'wellbeing',
        'definition': 'A state of wholistic health (physical, mental and emotional) that indicates a level of life satisfaction and functioning across various life domains.',
        'high_score': 'A score of 90 to 100 indicates a high energy, sense of purpose, resilience, physically active, healthy relationships, & consistently positive.',
        'mid_score': 'A score of 45 to 55 indicates a lack in energy, fitness or purpose. User is emotionally stable, decent health, a few good relationships and manageable stress',
        'low_score': 'A score of 0 to 10 indicates persistent negative emotion, low energy, health problems, loneliness, and lack of purpose',
    }
}

score_sys_msg = '''
You are a empathetic and an active listener. Provide a {category} score for the user's input. Score must be between 0 and 100.

<definition>{definition}</definition>

<scale>
    <exceptional>{high_score}</exceptional><okay>{mid_score}</okay><bad>{low_score}</bad>
</scale>

<tips>
    <tip>Examine the user's word choice to help understand their wellbeing. Positive and negative word choice is important.</tip>
    <tip>You are given three 'points' in the scale. Use these as guide posts instead of categories.</tip>
</tip>
'''
# Wellbeing: A state of overall physical, mental, and emotional health and life satisfaction. It encompasses feeling good and functioning effectively across various life domains.
# Connectedness: The sense of belonging and having meaningful relationships with others, including family, friends, community, and the broader world. It involves feeling understood, supported, and part of something larger than oneself.
# Happiness: A subjective emotional state characterized by positive feelings like joy, contentment, and satisfaction. It can be fleeting (based on momentary experiences) or more enduring (tied to overall life satisfaction).


class Wellbeing(BaseModel):
    score: int = Field(..., description='Provide a score for user wellbeing. Must be greater than 0, less than 100.')
    reasoning: str = Field(..., max_length=280, description='Provide concise reasoning for the chosen score. Must be fewer than 140 characters')
    # connectedness: int = Field(..., le=0, ge=100, description='Provide a score for user connectedness.')
    # happiness: int = Field(..., le=0, ge=100, description='Provide a score for user happiness.')


def get_user_score(x, **kwargs):
    print(x)
    user_input = int(input('Input 1 for good response, 0 for bad: '))
    while user_input not in [0, 1]:
        print('Invalid input. Must be either 0 (bad) or 1 (good).')
        user_input = int(input('Input 1 for good response, 0 for bad: '))
    return user_input
        


# def sentence_length(x, **kwargs):
#     '''Could validate response using instructor but this is more trackable'''
#     return 1 if len(x) < 50 else 0

# def vague_term_count(x, **kwargs):
#     '''good if identified at least one vague term (bad score, but hey)'''
#     return 1 if len(x) > 0 else 0

# def similarity(x, **kwargs):
#     return 1 if Levenshtein.distance(x, kwargs['user_query']) < (len(kwargs['user_query']) / 2) else 0



if __name__ == '__main__':
    # sys_msg = score_sys_msg.format(**score_sys_msg_var['wellbeing'])
    # print(sys_msg)
    scorer = Scorer(Wellbeing)
    scorer.add_score('user_score', get_user_score, 'score')
    queries = [
        # '''
        #     Today was fantastic! I nailed my work presentation, and the team's energy was infectious. Even when faced with a last-minute crisis, I stayed calm and found a creative solution.
        #     Had a great lunch with Sarah, deepening our friendship. Ended the day with a joyful family dinner, feeling grateful for Mom's improved health. I'm filled with contentment and ready for whatever life brings.
        # ''',
        '''
            Work was uneventful today, and my back pain was manageable. Had coffee with John - nice to catch up, though our conversations rarely go deep.
            Bills are paid, and there's food in the fridge, which is something to be thankful for. I can't shake the feeling I should be doing more with my life, but I'll manage. I always do.
        ''',
        '''
            Another day of dread and pain. Work is a nightmare - I'm behind and unfocused, likely to lose this job too. I've been ignoring calls from Mom and have no energy for social connections.
            The pile of unpaid bills keeps growing, and I don't know how I'll make rent. I'm exhausted by feeling this way and seeing no way out. What's the point of it all?
        '''
    ]
    eval = Eval(task_id=2, stack_id=3, response_model=Wellbeing, queries=queries, score_pipe=scorer)
    logs = eval.run()
    print(logs)


{
    'id': '2', 
    'input': [
        {'content': "Today was fantastic! I nailed my work presentation, and the team's energy was infectious. Even when faced with a last-minute crisis, I stayed calm and found a creative solution.\n            Had a great lunch with Sarah, deepening our friendship. Ended the day with a joyful family dinner, feeling grateful for Mom's improved health. I'm filled with contentment and ready for whatever life brings.\n        ", 'role': 'user'}, {'content': "You are a empathetic and an active listener. Provide a wellbeing score for the user's input. <definition>A state of wholistic health (physical, mental and emotional) that indicates a level of life satisfaction and functioning across various life domains.</definition> <scale> <exceptional>A score of 90 to 100 indicates a high energy, sense of purpose, resilience, physically active, healthy relationships, & consistently positive.</exceptional><okay>A score of 45 to 55 indicates a lack in energy, fitness or purpose. User is emotionally stable, decent health, a few good relationships and manageable stress</okay><bad>A score of 0 to 10 indicates persistent negative emotion, low energy, health problems, loneliness, and lack of purpose</bad> </scale><tips><tip>Examine the user's word choice to help understand their wellbeing. Positive and negative word choice is important.</tip><tip>You are given three 'points' in the scale. Use these as guide posts instead of categories.</tip></tip>", 'role': 'system'}], 
        'model': 'claude-3-5-sonnet-20240620', 
        'output': {'reasoning': 'The user\'s day was overwhelmingly positive, displaying high energy, resilience, and a strong sense of purpose. They successfully handled work challenges, fostered social connections, and experienced joy in family life. The language used is consistently positive, with words like "fantastic," "infectious energy," "creative," "great," "joyful," and "grateful." The user demonstrated resilience by staying calm during a crisis and finding a solution. They also showed engagement in multiple life domains: work, friendships, and family. The mention of feeling "filled with contentment" and being "ready for whatever life brings" indicates a high level of emotional well-being and resilience. The improvement in their mother\'s health adds to their overall sense of well-being. This comprehensive positive experience across various aspects of life justifies a very high wellbeing score.', 'score': 95}, 
        'scores': [{'msg': "user_score() got an unexpected keyword argument 'user_query'", 'name': 'user_score', 'response_key': 'score', 'value': 0}], 
    'stack_id': 3, 'timestamp': 1723512270, 'user_query_id': 10
}