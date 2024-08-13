from datetime import datetime
from enum import Enum
from typing import List, Optional, Literal, Any, Dict
from sqlmodel import SQLModel, Field, Relationship


class Task(SQLModel, table=True):
    __tablename__ = 'tasks'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)


class ModelEnum(str, Enum):
    SONNET = 'claude-3-5-sonnet-20240620' # advanced
    HAIKU = 'claude-3-haiku-20240307' # cheap, basic

class Stack(SQLModel, table=True):
    __tablename__ = 'stacks'
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key='tasks.id')
    name: str
    model: ModelEnum = Field(default=ModelEnum.HAIKU.value)
    user_prompt_template: Optional[str] = Field(default='{query}', description='User prompt template, must contain "{query}".')
    system_prompt: Optional[str] = Field(default=None, description='Hydrated system prompt')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def validate_user_prompt(self):
        if '{query}' not in self.user_prompt_template:
            raise ValueError('user template must contain "{query}"')


class StackCreate(SQLModel):
    task_id: int
    name: str
    model: Optional[ModelEnum] = None
    user_prompt_template: str
    system_prompt: Optional[str] = None


class Dataset(SQLModel, table=True):
    __tablename__ = 'datasets'
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key='tasks.id')
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DatasetCreate(SQLModel):
    task_id: int
    name: str
    description: Optional[str] = None


class UserQuery(SQLModel, table=True):
    __tablename__ = 'user_queries'
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: Optional[int] = Field(default=None, foreign_key='datasets.id')
    task_id: Optional[int] = Field(default=None, foreign_key='tasks.id')
    query: str
    r_user_query_stack: 'UserQueryStack' = Relationship(back_populates='r_user_query')

    
class UserQueryStack(SQLModel, table=True):
    __tablename__ = 'user_query_stacks'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_query_id: int = Field(default=None, foreign_key='user_queries.id')
    stack_id: int = Field(default=None, foreign_key='stacks.id')
    user_query_id: int
    r_user_query: 'UserQuery' = Relationship(back_populates='r_user_query_stack')


class Score(SQLModel, table=True):
    '''
    * aggregating by user_query will show progression on a specific user request
    * aggreating by stack will show a progression on a specific task
    '''
    __tablename__ = 'scores'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_query_id: int = Field(default=None, foreign_key='user_queries.id')
    stack_id: int = Field(default=None, foreign_key='stacks.id')
    name: str
    response_key: str
    value: int = Field(ge=0, le=1)
    msg: Optional[str] = Field(default=None)
    is_human_reviewed: bool = Field(default=False)
    timestamp: datetime = Field(default=datetime.utcnow())

class ScoreCreate(SQLModel):
    name: str
    response_key: str
    value: int = Field(ge=0, le=1)
    msg: Optional[str] = Field(default=None)


class Log(SQLModel):
    user_query_id: int
    stack_id: int
    model: str
    input: List[Dict[str, str]]
    output: Dict[str, Any] = Field(..., description='Output in form of user passed response_model')
    scores: List[ScoreCreate]
    timestamp: Optional[int] = None


# input = {
#     'model': None, 'messages': []
# }