import typesense
from .main import logger

log = {
    'name': 'logs',
    'enable_nested_fields': True,
    'fields': [
        {'name': 'user_query_id', 'type': 'int64'},
        {'name': 'stack_id', 'type': 'int64'},
        {'name': 'model', 'type': 'string'},
        {'name': 'input', 'type': 'object[]'},
        {'name': 'output', 'type': 'object'}, #just making it a string for simplifying logging
        {'name': 'scores', 'type': 'object[]'},
        {'name': 'timestamp', 'type': 'int64', 'sort': True}
    ]
}


def connect():
    return typesense.Client({
        'nodes': [{
            'host': 'localhost',
            'port': '8108',
            'protocol': 'http'
        }],
        'api_key': 'xyz',
        'connection_timeout_seconds': 2
    })

def create_collection(log):
    client = connect()
    try:
        client.collections['logs'].delete()
        client.collections.create(log)
        print('created \n\n\nn\n\n\n\n')
    except Exception as e:
        logger.error(f'Issue creating log collection: str({e})')


class DocumentCRUD:
    def __init__(self, collection_name: str = 'logs'):
        self.collection_name = collection_name
        self.client = connect()
    
    def add_document(self, data: dict):
        response = self.client.collections[self.collection_name].documents.create(data)
        return response

    def get_document(self, document_id: int):
        response = self.client.collections[self.collection_name].documents[document_id].retrieve()
        return response

    def search_documents(self, query: str, user_query_id: int = None, stack_id: int = None, limit: int = 10):
        query = {'sort_by': 'timestamp:desc', 'limit': limit, 'query_by': '*', 'q': query}
        f_user_q = f'user_query_id:{user_query_id}'
        f_stack = f'stack_id:{stack_id}'
        # https://typesense.org/docs/26.0/api/search.html#query-parameters
            # probz just include key filter logic in separate method
        if user_query_id and stack_id:
            query['filter_by'] = f'{f_user_q} && {f_stack}'
        elif stack_id:
            query['filter_by'] = f_stack
        elif user_query_id:
            query['filter_by'] = f_user_q

        results = self.ts_client.collections[self.collection_name].documents.search(query)
        return results['hits']
