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
        self.database_path = "postgres://{}/{}".format('student:student@localhost:5432', self.database_name)
        
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
        
    def test_404_get_categories_with_id(self):
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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()