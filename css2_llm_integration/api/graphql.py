from ariadne.asgi import GraphQL
from ariadne_graphql_modules import ObjectType, gql, make_executable_schema, convert_case, DeferredType


class CustomerType(ObjectType):
    __schema__ = gql(
        """
        type Customer {
            id: ID!
            firstName: String,
            lastName: String,
            email: String,
            phone: String
        }
        """
    )
    __aliases__ = convert_case

class CustomerQuery(ObjectType):
    __requires__ = [DeferredType("Customer")]
    __schema__ = gql(
        """
        type Query {
            customer(id: ID!): Customer
            customers: [Customer!]!
        }
        """
    )


class Query(ObjectType):
    __schema__ = gql(
        """
        type Query {
            search_customers(search_customers_type: SearchCustomersType!): 
        }
        """
    )

    __fields_args__ = convert_case