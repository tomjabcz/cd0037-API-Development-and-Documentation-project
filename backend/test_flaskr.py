import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('student:student@localhost:5432', self.database_name)
        
        self.database_path = "postgresql://{}:{}@{}:{}/{}".format(
            os.getenv('DB_USER', 'student'),
            os.getenv('DB_PASSWORD', 'student'),
            os.getenv('DB_HOST', 'localhost'),
            os.getenv('DB_PORT', '5432'),
            self.database_name
        )



        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client
        self.new_question = {"question": "What is the best place to live in?", "answer": "Czech Republic", "category": 3, "difficulty": 4}

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["categories"], 
            { 
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports" 
            }
        )
        
    def test_404_get_categories_with_wrong_id(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data, 
            {
                "error": 404, 
                "message": "resource not found", 
                "success": False
            }
        )


    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["categories"], 
            { 
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports" 
            }
        )
        self.assertEqual(data["totalQuestions"],19) 
        self.assertEqual(len(data["questions"]),10) 
 

    def test_get_questions_paginate(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["categories"], 
            { 
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports" 
            }
        )
        self.assertEqual(data["totalQuestions"],19) 
        self.assertEqual(len(data["questions"]),10)


    def test_get_questions_paginate_out_of_range(self):
        res = self.client().get("/questions?page=999")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["categories"], 
            { 
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports" 
            }
        )
        self.assertEqual(data["totalQuestions"],19) 
        self.assertEqual(len(data["questions"]),0)
        
        

    def test_post_question_search(self):
        res = self.client().post("/questions", json={"searchTerm":"title"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["totalQuestions"],2) 
        self.assertEqual(len(data["questions"]),2)
        self.assertTrue(data["currentCategory"])
        
                

    def test_post_question_search_non_existent(self):
        res = self.client().post("/questions", json={"searchTerm":"title22"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["totalQuestions"],0) 
        self.assertEqual(len(data["questions"]),0)
        self.assertTrue(data["currentCategory"])
        

    
    def test_post_question_and_delete(self):
        # add new question
        res = self.client().post("/questions", json={"question":"test question","answer":"test answer","difficulty":1,"category":1})
        data = json.loads(res.data)
        question_id = data["question_id"]
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"],"test question")
        self.assertEqual(data["answer"], "test answer")
        self.assertTrue(data["question_id"])
        # delete new question
        res = self.client().delete("/questions/"+str(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        # confirm deletion
        res = self.client().delete("/questions/"+str(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        
    

    def test_delete_question_with_wrong_id(self):
        res = self.client().delete("/questions/999")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_list_questions_in_a_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        
    def test_list_questions_in_a_category_out_of_range(self):
        res = self.client().get("/categories/999/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    
    def test_quizzes_id1_empty(self):
        res = self.client().post("/quizzes", json={'previous_questions': [], "quiz_category":{"type":"Science","id":1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["question"]), 5)
        self.assertTrue(data["question"])
        
    def test_quizzes_id1_no_more_questions(self):
        res = self.client().post("/quizzes", json={'previous_questions': [20, 21, 22], "quiz_category":{"type":"Science","id":1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["question"]), 0)
        self.assertEqual(data["question"],"")

    
    def test_quizzes_ALL_empty(self):
        res = self.client().post("/quizzes", json={'previous_questions': [], "quiz_category":{"type":"click","id":0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["question"]), 5)
        self.assertTrue(data["question"])

    def test_quizzes_wrong_category_empty(self):
        res = self.client().post("/quizzes", json={'previous_questions': [], "quiz_category":{"type":"click","id":999}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()