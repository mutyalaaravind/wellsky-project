import os

from ariadne import MutationType, ObjectType, QueryType, InputType, gql, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Mount

from formographer.usecases import resolvers
from formographer.usecases.types import FormField

query = QueryType()
query.set_field('version', resolvers.get_version)

mutation = MutationType()
mutation.set_field('complete_form', resolvers.complete_form)


class GraphQLAdapter(Starlette):
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.graphql')

    def __init__(self):
        with open(self.SCHEMA_PATH, encoding='utf-8') as fobj:
            schema_source = fobj.read()

        schema = make_executable_schema(
            gql(schema_source),
            query,
            mutation,
            # Add all custom types here...
            InputType('FormField', lambda data: FormField(**data)),
            # result,
        )
        graphql = GraphQL(schema, debug=True)

        super().__init__(
            debug=True,
            routes=[
                Mount('', graphql),
            ],
        )
