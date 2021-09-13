import graphene

from fastapi import FastAPI
from starlette.graphql import GraphQLApp

app = FastAPI()


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name


app.add_route("/", GraphQLApp(schema=graphene.Schema(query=Query)))
