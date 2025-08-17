import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation
import crm.schema

class Query(crm.schema.Query, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
