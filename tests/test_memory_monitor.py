import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.comparison import MemoryMonitor, app

class TestMemoryMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = MemoryMonitor()
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def test_memory_stats(self):
        """Test if memory statistics are properly retrieved"""
        stats = self.monitor.get_memory_stats()
        
        # Check if all required keys are present
        required_keys = ['total', 'available', 'used', 'free', 'percent', 
                        'swap_total', 'swap_used', 'swap_free', 'swap_percent']
        for key in required_keys:
            self.assertIn(key, stats)
        
        # Check if values are valid
        self.assertGreater(stats['total'], 0)
        self.assertGreaterEqual(stats['percent'], 0)
        self.assertLessEqual(stats['percent'], 100)

    def test_cache_stats(self):
        """Test if cache statistics are properly simulated"""
        stats = self.monitor.get_cache_stats()
        
        # Check if all required keys are present
        required_keys = ['hits', 'misses', 'hit_ratio', 'access_time', 
                        'eviction_rate', 'write_back_rate']
        for key in required_keys:
            self.assertIn(key, stats)
        
        # Check if values are within expected ranges
        self.assertGreaterEqual(stats['hits'], 80)
        self.assertLessEqual(stats['hits'], 95)
        self.assertGreaterEqual(stats['hit_ratio'], 0.8)
        self.assertLessEqual(stats['hit_ratio'], 0.95)

    def test_performance_metrics(self):
        """Test if performance metrics are properly generated"""
        metrics = self.monitor.get_performance_metrics()
        
        # Check if all required keys are present
        required_keys = ['response_time', 'throughput', 'page_faults', 'swap_rate']
        for key in required_keys:
            self.assertIn(key, metrics)
        
        # Check if values are within expected ranges
        self.assertGreaterEqual(metrics['response_time'], 0.1)
        self.assertLessEqual(metrics['response_time'], 2.0)
        self.assertGreaterEqual(metrics['throughput'], 1000)
        self.assertLessEqual(metrics['throughput'], 5000)

    def test_record_stats(self):
        """Test if statistics are properly recorded"""
        initial_length = len(self.monitor.memory_history)
        self.monitor.record_stats()
        
        # Check if new records were added
        self.assertEqual(len(self.monitor.memory_history), initial_length + 1)
        self.assertEqual(len(self.monitor.cache_history), initial_length + 1)
        self.assertEqual(len(self.monitor.timestamps), initial_length + 1)

if __name__ == '__main__':
    unittest.main() 