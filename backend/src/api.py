from crypt import methods
import os
from select import select
from selectors import SelectSelector
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    selection = Drink.query.all()
    return jsonify({
        'success': True,
        'status_code': 200,
        "drinks": [drinks.short() for drinks in selection]
    })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
def get_drinks_detail():
    selection = Drink.query.all()
    # drinks = selection.long()
    return jsonify({
        'success': True,
        'status_code': 200,
        "drinks": [drinks.long() for drinks in selection]
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drinks():
    body = request.get_json()
    recipe = [{}]

    title = body.get('title')
    color = body.get('color')
    name = body.get('name')
    parts = body.get('parts')

    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe[0]['color'] = color
    recipe[0]['name'] = name
    recipe[0]['parts'] = parts

    if (body, title, recipe, color, parts) == None:
        abort(42)

    try:
        drink = Drink(
            title =title,
            recipe = recipe,
        )

        drink.insert()
        drinks =  db.session.query(Drink).filter(Drink.id == drink.id).one_or_none()

        return jsonify({
            'success': True,
            'status_code': 200,
            "drinks": [drinks.long()]
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
def edit_drink(id):
    body = request.get_json()
    if request.method == 'PATCH':
        try:
            selection = db.session.query(Drink).filter(Drink.id == id).one_or_none()

            title = body.get('title')
            color = body.get('color')
            name = body.get('name')
            parts = body.get('parts')

            selection.title = title
            selection.recipe[0]['color'] = color
            selection.recipe[0]['name'] = name
            selection.recipe[0]['parts'] = parts

            drink = selection.update()
            drinks =  db.session.query(Drink).filter(Drink.id == drink.id).one_or_none()

            return jsonify({
                'success': True,
                'status_code': 200,
                "drinks": [drinks.long()]
            })

        except:
            abort(404)





'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    if request.method == 'DELETE':
        try:
            drink = db.session.query(Drink).filter(Drink.id == id).one_or_none()
            drink.delete()

            return jsonify({
                'success': True,
                'id': id
            })
        except:
            abort(404)



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "message": "You are not authorized to access this content"
    })
