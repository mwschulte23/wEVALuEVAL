from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from ...database import get_session
from ...main import logger
from ...search import DocumentCRUD
from ...models.models import (
    Task, TaskCreate,
    Stack, StackCreate,
    UserQuery, UserQueryStack,
    Score, ScoreCreate,
    Dataset, DatasetCreate,
    Log
)


task_router = APIRouter()

def simple_write(object, session):
    session.add(object)
    session.commit()
    session.refresh(object)
    return object


@task_router.post('/', tags=['Setup'])
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    try:
        db_task = Task(**task.model_dump())
        return simple_write(db_task, session)
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get('/{task_id}', tags=['Setup'])
async def create_task(task_id: int, session: Session = Depends(get_session)):
    try:
        return session.get(Task, task_id)
    except Exception as e:
        logger.error(f"Failed to get task: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@task_router.post('/stack/', tags=['Setup'])
async def create_stack(stack: StackCreate, session: Session = Depends(get_session)):
    try:
        db_stack = Stack(**stack.model_dump())
        db_stack.validate_user_prompt()
        return simple_write(db_stack, session)
    except Exception as e:
        logger.error(f"Failed to create stack: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get('/stack/{stack_id}', response_model=Stack, tags=['Setup'])
async def get_stack(stack_id: int, session: Session = Depends(get_session)):
    try:
        return session.get(Stack, stack_id)
    except Exception as e:
        logger.error(f"Failed to get run: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


# DURING RUN
@task_router.post('/query/bulk', tags=['Eval Run'])
async def create_queries(stack_id: int, task_id: int, queries: List[str], session: Session = Depends(get_session)):
    try:
        user_queries = [UserQuery(query=query, task_id=task_id) for query in queries]
        session.add_all(user_queries)
        session.flush()  # Flush to ensure all UserQuery IDs are populated
        out_queries = {q.query: q.id for q in user_queries}
        for user_query in user_queries:
            session.add(UserQueryStack(stack_id=stack_id, user_query_id=user_query.id))
        session.commit()
        return out_queries
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to bulk import queries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to import queries")


@task_router.post('/query/score', tags=['Eval Run'])
async def add_score(user_query_id: int, stack_id: int, score: ScoreCreate, session: Session = Depends(get_session)):
    try:
        score = Score(user_query_id=user_query_id, stack_id=stack_id, **score.model_dump())
        return simple_write(score, session)
    except Exception as e:
        logger.error(f"Failed to post score: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to post score")


@task_router.post('/log/', tags=['Eval Run'])
async def log_llm_call(log: Log):
    try:
        #TODO link to log metadata that writes to db
        log.timestamp = int(datetime.utcnow().timestamp())
        doc_crud = DocumentCRUD()
        return doc_crud.add_document(log.model_dump())
    except Exception as e:
        logger.error(f"Failed to post logs to typesense: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to post logs to typesense")


# POST RUN
@task_router.post('/dataset/', response_model=Dataset)
async def create_dataset(dataset: DatasetCreate, session: Session = Depends(get_session)):
    try:
        db_dataset = Dataset(**dataset.model_dump())
        return simple_write(db_dataset, session)
    except Exception as e:
        logger.error(f"Failed to create dataset: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create dataset")

@task_router.get('/dataset/{dataset_id}')
async def get_dataset(dataset_id: int, session: Session = Depends(get_session)):
    return session.get(Dataset, dataset_id)


@task_router.put('/query/{user_query_id}/{dataset_id}')
async def add_query_to_dataset(user_query_id: int, dataset_id: int, session: Session = Depends(get_session)):
    db_user_query = session.get(UserQuery, user_query_id)
    db_user_query.dataset_id = dataset_id
    return simple_write(db_user_query, session)

@task_router.get('/query/{user_query_id}')
async def get_user_query(user_query_id: int, session: Session = Depends(get_session)):
    return session.get(UserQuery, user_query_id)



@task_router.get('/query/list', response_model=List[UserQuery])
async def list_queries(stack_id: int = None, limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    try:
        statement = select(UserQuery).join(UserQueryStack).where(
            UserQuery.id == UserQueryStack.user_query_id,
            UserQueryStack.stack_id == stack_id
        )
        # if stack_id:
        #     statement = statement.where(UserQuery.stack_id == stack_id)
        resp = session.exec(statement.limit(limit).offset(offset)).all()
        print(resp)
        return resp
    except Exception as e:
        logger.error(f"Failed to bulk import runs: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get queries")
