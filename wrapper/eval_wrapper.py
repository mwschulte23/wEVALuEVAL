import requests
import instructor
import anthropic

from typing import Any, Callable, Dict, List, Literal, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from scorer_pipe import Scorer



#TODO wrapper code for task and stack creation that easily works here

class Eval:
    def __init__(self, task_id: int, stack_id: int, response_model: BaseModel, queries: List[str], score_pipe: Scorer = None):
        self.base_url = 'http://localhost:8000/api/v1/task'
        self.task_id = task_id
        self.stack_id = stack_id
        self.response_model = response_model
        self.queries = queries
        self.score_pipe = score_pipe
        self.stack = self.get_stack()

    def get_stack(self):
        resp = requests.get(f'{self.base_url}/stack/{self.stack_id}')
        if resp.status_code != 200:
            raise 'Failed to get stack'
        return resp.json()
    
    def write_queries(self) -> List[Dict[str, int]]:
        resp = requests.post(f'{self.base_url}/query/bulk?stack_id={self.stack_id}&task_id={self.task_id}', json=self.queries)
        if resp.status_code != 200:
            raise 'Issue posting queries'
        return resp.json()

    def format_messages(self, query):
        messages = [{'role': 'user', 'content': self.stack['user_prompt_template'].format(query=query)}]
        if self.stack.get('system_prompt'):
            messages.append({'role': 'system', 'content': self.stack['system_prompt']})
        return messages


    def call_llm(self, messages):
        client = instructor.from_anthropic(anthropic.Anthropic())
        return client.chat.completions.create(
            model=self.stack.get('model'),
            messages=messages,
            response_model=self.response_model,
            max_tokens=1024
        )
        

    def _write_scores(self, score: BaseModel, query_id: int):
        resp = requests.post(
            f'{self.base_url}/query/score?user_query_id={query_id}&stack_id={self.stack_id}',
            json=score
        )
        return resp.json()
    
    def calculate_scores(self, llm_response: dict, query: str, query_id: int):
        if self.score_pipe:
            scores = self.score_pipe.score(llm_response, user_query=query)
            for score in scores:
                self._write_scores(score, query_id)
        else:
            scores = []
            # TODO log this code ran
        return scores

    def log_call(self, user_query_id, prompts, output, scores):
        log_data = {
            'user_query_id': user_query_id,
            'stack_id': self.stack_id,
            'model': self.stack.get('model'),
            'input': prompts,
            'output': output,
            'scores': scores
        }
        resp = requests.post(f'{self.base_url}/log/', json=log_data)
        if resp.status_code != 200:
            print('what the heck man!')
        return resp.json()
        
    
    def process_query(self, query, query_id):
        '''
        Single query / llm call / log / etc
        '''
        messages = self.format_messages(query)
        llm_response = self.call_llm(messages)
        llm_response_dict = llm_response.model_dump() # SEPARATING IN CASE OF PYDANTIC METHODS
        scores = self.calculate_scores(llm_response_dict, query, query_id)
        return self.log_call(user_query_id=query_id, prompts=messages, output=llm_response_dict, scores=scores)

    def run(self):
        loaded_queries = self.write_queries()

        logs = []
        for query in self.queries:
            query_id = loaded_queries[query]
            log = self.process_query(query, query_id)
            logs.append(log)
        return logs
