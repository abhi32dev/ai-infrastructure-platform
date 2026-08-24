import unittest
import os
import sys

# Ensure backend import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.harvesters.greenhouse import fetch_greenhouse_jobs
from backend.harvesters.lever import fetch_lever_jobs
from backend.harvesters.ashby import fetch_ashby_jobs
from backend.database import save_jobs, query_jobs

class TestHarvesters(unittest.TestCase):

    def test_greenhouse_harvester(self):
        jobs = fetch_greenhouse_jobs("stripe", "Stripe")
        self.assertIsInstance(jobs, list)
        if jobs:
            self.assertEqual(jobs[0]["company"], "Stripe")
            self.assertEqual(jobs[0]["ats_provider"], "Greenhouse")
            self.assertTrue(jobs[0]["apply_url"].startswith("http"))

    def test_lever_harvester(self):
        jobs = fetch_lever_jobs("spotify", "Spotify")
        self.assertIsInstance(jobs, list)
        if jobs:
            self.assertEqual(jobs[0]["company"], "Spotify")
            self.assertEqual(jobs[0]["ats_provider"], "Lever")

    def test_ashby_harvester(self):
        jobs = fetch_ashby_jobs("notion", "Notion")
        self.assertIsInstance(jobs, list)
        if jobs:
            self.assertEqual(jobs[0]["company"], "Notion")
            self.assertEqual(jobs[0]["ats_provider"], "Ashby")

    def test_database_save_and_query(self):
        test_job = [{
            "id": "test_123",
            "company": "TestCorp",
            "title": "Senior Python Architect",
            "location": "San Francisco, CA",
            "apply_url": "https://jobs.testcorp.com/123",
            "description": "Test job description for Python and AWS",
            "ats_provider": "Greenhouse",
            "posted_date": "2026-08-23"
        }]
        saved = save_jobs(test_job)
        self.assertGreater(saved, 0)
        
        results = query_jobs(search_query="Python")
        self.assertGreater(len(results), 0)

if __name__ == "__main__":
    unittest.main()
