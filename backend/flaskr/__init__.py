import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import or_
from models import setup_db, Question, Category
import json

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

      
    
    """
    DONE @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*" : {"origins": '*'}})

    """
    DONE @TODO: Use the after_request decorator to set Access-Control-Allow
        
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    """
    DONE @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        
        selection = Category.query.order_by(Category.id).all()
        formatted_selection = [category.format() for category in selection]
     
        #output_selection = {'categories': {str(item['id']): item['type'] for item in formatted_selection}}
        output_selection = {str(item['id']): item['type'] for item in formatted_selection}
        
        return jsonify(
            {
                "categories": output_selection
            }
        )
        

    """
    DONE @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
                       
        selection_category = Category.query.order_by(Category.id).all()
        formatted_selection_category = [category.format() for category in selection_category]
        output_selection = {str(item['id']): item['type'] for item in formatted_selection_category}
        
        return jsonify(
            {
                "questions": current_questions,
                "totalQuestions": len(selection),
                "categories": output_selection,
                "currentCategory": "History"

            }
        )


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        

        return jsonify(
            {
                "success": True,
                "deleted": question_id,                
            }
        )



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def search_questions():
        body = request.get_json()

        if 'searchTerm' in body:
            search_term = body["searchTerm"]
            selection = Question.query.filter(or_(Question.question.ilike(f'%{search_term}%'),Question.answer.ilike(f'%{search_term}%'))).all()
            formatted_selection = [question.format() for question in selection]
            
            output =  jsonify(
                {
                    "questions": formatted_selection,
                    "totalQuestions": len(selection),
                    "currentCategory": "History"

                }
            )
            return output

        else:
                        
            question_text = body.get("question", None)
            answer = body.get("answer", None)
            difficulty = body.get("difficulty", None)
            category = body.get("category", None)
        
            question = Question(question=question_text, answer=answer, difficulty=difficulty, category = category)
            question.insert()
            
                           
            return jsonify (
                {
                    "answer": answer, 
                    "category": category, 
                    "difficulty": difficulty, 
                    "question": question_text,
                    "question_id": question.id
                }
            )



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_by_id(category_id):
        
        selection = Question.query.filter(Question.category == category_id).all()
        
               
        if len(selection) == 0:
            abort(404)
        
        
        questions = [question.format() for question in selection]
         
        category = Category.query.filter(Category.id == category_id).one_or_none().format()
              
        return jsonify(
            {
                "questions": questions,
                "totalQuestions": len(selection),
                "currentCategory": category['type']

            }
        )




    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def give_question():
        
        body = request.get_json()
        previous_questions = body["previous_questions"] 
        category = body["quiz_category"]["id"]

        # if category == ALL, do not filter
        if category == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category).all()

        # give question which is not in the previous_questions 
        
        question = None
        
        for q in questions:
            if q.id not in previous_questions:
                question = q
                break 
        
        # if there are no more questions return empty response
        if question is None:
            return jsonify({"question": ""})
     
        # otherwise format question and return
        formatted_question = question.format() 
        
        return jsonify({"question": formatted_question})


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": 500, "message": "internal Server Error"}), 500

    return app

