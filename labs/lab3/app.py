from ariadne import ObjectType, QueryType, MutationType, graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = "secret key"

studentId = 1
classId = 1

studentKey = "_student"
classKey = "_class"
session = {}
type_defs = """
    type Query {
        students(id: Int!): Student
        classes(id: Int!): Class
    }
    type Student {
        id: ID!
        name: String!
    }
    type Class {
        id: ID!
        name: String!
        students: [Student!]!
    }
    type Mutation {
        createStudent(name: String!): Student
        createClass(name: String!): Class
        addStudentToClass(classID: Int!, studentID: Int!): Class
    }
    
"""

query = QueryType()
mutation = MutationType()

@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code

@query.field("students")
def resolve_students(*_, id):
    print(session.keys())
    if (str(id)+studentKey in session.keys()):
        return session[str(id)+studentKey]

@mutation.field("createStudent")
def resolve_createStudent(*_, name):
    global studentId

    studentID = studentId

    studentId += 1

    session[str(studentID)+studentKey] = {
        'id' : studentID,
        'name' : name
    }
    
    print(session[str(studentID)+studentKey])
    return session[str(studentID)+studentKey]

@query.field("classes")
def resolve_classes(*_, id):
    if (str(id)+classKey in session.keys()):
        return session[str(id)+classKey]

@mutation.field("createClass")
def resolve_createClass(*_, name):
    global classId

    classID = classId

    classId += 1

    session[str(classID)+classKey] = {
        "id" : classID,
        "name" : name,
        "students" : []
    }

    return session[str(classID)+classKey]

@mutation.field("addStudentToClass")
def addStudentIntoClass(*_, classID, studentID):
    if str(classID)+classKey in session.keys() and str(studentID)+studentKey in session.keys():
        student = session[str(studentID)+studentKey]
        session[str(classID)+classKey]['students'].append(student)
        return session[str(classID)+classKey]

schema = make_executable_schema(type_defs, [query, mutation])