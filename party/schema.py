#Graphene api

# Step 1 : Import
# - graphene, 
# - Graphene containers to send data in form of object or array of object,
# - App models which represent data objects
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphql_auth import mutations
from graphql_auth.schema import UserQuery, MeQuery
from .models import Party, Participant, Item, User

#graphql-auth mutation class
class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()

# Step 2 : Build object types which you want to o/p from the api
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'image', 'mobile_no']

class ParticipantType(DjangoObjectType):
    class Meta:
        model = Participant
        #parties = models.ManyToManyField(Party)
        fields = ['end_user', 'contribution', 'balance']    # end_user is a forgein key here, thus the object stemming from this forgein key (UserType) must be defined first.
        
class PartyType(DjangoObjectType):
    class Meta:
        model = Party
        fields = ['id','name', 'theme', 'venue', 'start_date', 'end_date', 'total_cost', 'total_contribution', 'total_purchase', 'description', 'status']

class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        # parties = models.ManyToManyField(Party)
        # consumers = models.ManyToManyField(Participant)
        fields = ['id','name', 'category', 'quantity', 'price', 'purchased', 'for_all', 'consumers']

# Step 3.1 : Define Query classes which hanldes queries on the server.
class Query(UserQuery, MeQuery, graphene.ObjectType):
    # Declaring functions which you want to query.
    all_parties = graphene.List(PartyType)
    party_by_name = graphene.List(PartyType, name=graphene.String(required=True)) # Parameterized function
    party_by_id = graphene.Field(PartyType, id=graphene.ID(required=True))
    all_items = graphene.List(ItemType)
    party_items = graphene.List(ItemType, id=graphene.ID(required=True))
    party_participants = graphene.List(ParticipantType, id=graphene.ID(required=True))
    
    # Define functions to "resolve" the query (Resolvers)
    def resolve_all_parties(root, info):
        return Party.objects.all()
    
    # do exception handling here.
    def resolve_party_by_id(root, info, id):
        return Party.objects.get(pk=id) 
    
    def resolve_party_by_name(root, info, name):
        return Party.objects.filter(name__contains=name)

    def resolve_all_items(root, info):
        return Item.objects.all()
    
    def resolve_party_items(root, info, id):
        return Item.objects.filter(parties=id)

    def resolve_party_participants(root, info, id):
        return Participant.objects.filter(parties=id)

# Step 3.2 : Define Mutation class to make changes in the database invoked by the frontend
class Mutation(AuthMutation, graphene.ObjectType):
    pass

# Step 4 : Finalize the schema
schema = graphene.Schema(query=Query, mutation=Mutation)


'''
Sample query :
query PartyInfo($id : ID = "1"){
  partyById(id : $id)
  {
  	name
    venue
    status
    startDate
  }
  partyItems(id : $id)
  {
    name
    price
    quantity
    category
    consumers{
      user{
        firstName
        lastName
      }
    }
    
  }
  partyParticipants(id : $id)
  {
  	contribution
  	user{
      firstName
      lastName
    }
  }
}

Query to check user info :
query{
    users{
        edges{
            node{
                email
                firstName
                lastName
            }
        }
    }
}

Query to check currently logged in user info :
query{
  me{
    username
    email
  }
}

Mutation to create new account : 
mutation{
  register(
    email : "ramona.flowers@gmail.com",
    username : "ramonaflowers",
    password1 : "poiuytrewq123",
    password2 : "poiuytrewq123"
  ){
    success,
    errors,
    token,
    refreshToken,
  }
}

Mutation to verify account (upon registeration):
mutation{
	verifyAccount(token : "hash token sent in the email")
	{
    success
    errors
  }
}

Mutation to login :
mutation{
  tokenAuth(
    username: "admin",
    password: "admin"
  )
  {
    success,
    errors,
    token,
    refreshToken
    user{
      username
      firstName
      lastName
      email
    }
  }
}
'''
