from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()


class ScoreFunction(BaseModel):
    name: str
    score_function: Callable
    response_key: str
    returns_msg: bool = Field(default=False)

class Score(BaseModel):
    name: str
    response_key: str
    value: int = Field(ge=0, le=1)
    msg: Optional[str] = Field(default=None)


class Scorer:
    def __init__(self, response_model):
        self.scorers = []
        self.response_model_keys = response_model.schema()['properties'].keys()
    
    def add_score(self, name: str, scorer: Callable, response_key: str):
        if response_key not in self.response_model_keys:
            raise f'{response_key} not in defined output schema'
        self.scorers.append(ScoreFunction(name=name, score_function=scorer, response_key=response_key))
    
    def score(self, response: Dict, **kwargs):
        scores = []
        for scorer in self.scorers:
            msg = None
            try:
                if scorer.returns_msg:
                    value, msg = scorer.score_function(response[scorer.response_key], **kwargs)
                else:
                    value = scorer.score_function(response[scorer.response_key], **kwargs)
            except Exception as e:
                value = 0
                msg = str(e)
            scores.append(Score(name=scorer.name, response_key=scorer.response_key, value=value, msg=msg).model_dump())
        return scores
