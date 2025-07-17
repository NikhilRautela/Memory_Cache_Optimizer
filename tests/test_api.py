import unittest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.comparison import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def test_index_route(self):
        """Test if the index route returns the template"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Memory & Cache Monitor', response.data)

    def test_real_time_stats(self):
        """Test if real-time stats endpoint returns proper data"""
        response = self.app.get('/api/real-time-stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Check if response contains required sections
        self.assertIn('memory', data)
        self.assertIn('cache', data)
        self.assertIn('timestamp', data)

    def test_optimize_memory(self):
        """Test if memory optimization endpoint works properly"""
        response = self.app.get('/api/optimize-memory')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Check if response contains before/after stats
        self.assertIn('before', data)
        self.assertIn('after', data)
        self.assertIn('improvement', data)
        
        # Verify optimization results
        self.assertLess(data['after']['percent'], data['before']['percent'])

    def test_optimize_cache(self):
        """Test if cache optimization endpoint works properly"""
        response = self.app.get('/api/optimize-cache')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Check if response contains before/after stats
        self.assertIn('before', data)
        self.assertIn('after', data)
        self.assertIn('improvement', data)
        
        # Verify optimization results
        self.assertGreater(data['after']['hit_ratio'], data['before']['hit_ratio'])

    def test_visualization(self):
        """Test if visualization endpoint returns proper data"""
        response = self.app.get('/api/visualization')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Check if response contains Plotly figure data
        self.assertIn('data', data)
        self.assertIn('layout', data)
        
        # Check if all required charts are present
        self.assertGreaterEqual(len(data['data']), 4)  # At least 4 charts
        self.assertIn('subplot_titles', data['layout'])

    def test_error_handling(self):
        """Test if error handling works properly"""
        # Test 404 error
        response = self.app.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main() 