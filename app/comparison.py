from flask import Flask, jsonify, render_template
import time
import numpy as np
from datetime import datetime
import logging
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app.models import MemoryStats, CacheStats, PerformanceMetrics, MemoryOptimizer, CacheOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with correct template and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, static_url_path='/static')

class MemoryMonitor:
    def __init__(self):
        self.memory_history = []
        self.cache_history = []
        self.timestamps = []
        self.optimization_history = {
            'memory': {'before': None, 'after': None, 'details': []},
            'cache': {'before': None, 'after': None, 'details': []}
        }
        self.performance_metrics = {
            'response_times': [],
            'throughput': [],
            'page_faults': [],
            'swap_usage': []
        }

    def get_memory_stats(self):
        memory_stats = MemoryStats.get_current()
        return memory_stats.to_dict()

    def get_cache_stats(self):
        cache_stats = CacheStats.get_current()
        return cache_stats.to_dict()

    def get_performance_metrics(self):
        metrics = PerformanceMetrics.get_current()
        return metrics.to_dict()

    def record_stats(self):
        try:
            memory_stats = self.get_memory_stats()
            cache_stats = self.get_cache_stats()
            metrics = self.get_performance_metrics()
            
            self.memory_history.append(memory_stats)
            self.cache_history.append(cache_stats)
            
            self.performance_metrics['response_times'].append(metrics['response_time'])
            self.performance_metrics['throughput'].append(metrics['throughput'])
            self.performance_metrics['page_faults'].append(metrics['page_faults'])
            self.performance_metrics['swap_usage'].append(metrics['swap_rate'])
            
            self.timestamps.append(datetime.now())
            
            # Limit history length
            max_history = 60  # 1 minute at 1 second intervals
            if len(self.memory_history) > max_history:
                self.memory_history = self.memory_history[-max_history:]
                self.cache_history = self.cache_history[-max_history:]
                self.timestamps = self.timestamps[-max_history:]
                self.performance_metrics['response_times'] = self.performance_metrics['response_times'][-max_history:]
                self.performance_metrics['throughput'] = self.performance_metrics['throughput'][-max_history:]
                self.performance_metrics['page_faults'] = self.performance_metrics['page_faults'][-max_history:]
                self.performance_metrics['swap_usage'] = self.performance_metrics['swap_usage'][-max_history:]
        except Exception as e:
            logger.error(f"Error recording stats: {str(e)}")

# Initialize the monitor
monitor = MemoryMonitor()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/real-time-stats')
def get_real_time_stats():
    try:
        monitor.record_stats()
        return jsonify({
            'memory': monitor.memory_history[-1],
            'cache': monitor.cache_history[-1],
            'timestamp': monitor.timestamps[-1].strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.error(f"Error getting real-time stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/optimize-memory')
def optimize_memory():
    try:
        before_stats = monitor.get_memory_stats()
        monitor.optimization_history['memory']['before'] = before_stats
        
        # Perform real memory optimization with details
        success, message, details = MemoryOptimizer.optimize_with_details()
        monitor.optimization_history['memory']['details'] = details
        
        if not success:
            logger.warning(f"Memory optimization failed: {message}")
            return jsonify({
                'success': False,
                'message': message,
                'before': before_stats,
                'after': before_stats,
                'details': details,
                'improvement': {
                    'before_ratio': before_stats['percent'],
                    'after_ratio': before_stats['percent'],
                    'improvement': 0
                }
            })
        
        # Get memory stats after optimization
        after_stats = monitor.get_memory_stats()
        monitor.optimization_history['memory']['after'] = after_stats
        
        return jsonify({
            'success': True,
            'message': message,
            'before': before_stats,
            'after': after_stats,
            'details': details,
            'improvement': compare_performance(
                before_stats['percent'],
                after_stats['percent']
            )
        })
    except Exception as e:
        logger.error(f"Error optimizing memory: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error during memory optimization: {str(e)}",
            'error': str(e)
        }), 500

@app.route('/api/optimize-cache')
def optimize_cache():
    try:
        before_stats = monitor.get_cache_stats()
        monitor.optimization_history['cache']['before'] = before_stats
        
        # Perform real cache optimization with details
        success, message, details = CacheOptimizer.optimize_with_details()
        monitor.optimization_history['cache']['details'] = details
        
        if not success:
            logger.warning(f"Cache optimization failed: {message}")
            return jsonify({
                'success': False,
                'message': message,
                'before': before_stats,
                'after': before_stats,
                'details': details,
                'improvement': {
                    'before_ratio': before_stats['hit_ratio'],
                    'after_ratio': before_stats['hit_ratio'],
                    'improvement': 0
                }
            })
        
        # Get cache stats after optimization
        after_stats = monitor.get_cache_stats()
        
        # No artificial improvements - show real stats
        logger.info("Using real cache statistics without artificial improvements")
        
        monitor.optimization_history['cache']['after'] = after_stats
        
        return jsonify({
            'success': True,
            'message': message,
            'before': before_stats,
            'after': after_stats,
            'details': details,
            'improvement': compare_performance(
                before_stats['hit_ratio'],
                after_stats['hit_ratio']
            )
        })
    except Exception as e:
        logger.error(f"Error optimizing cache: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error during cache optimization: {str(e)}",
            'error': str(e)
        }), 500

@app.route('/api/visualization')
def get_visualization():
    try:
        # Create visualization using plotly with more charts
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Memory Usage Over Time',
                'Cache Performance Over Time',
                'Memory Usage Comparison',
                'Cache Hit/Miss Ratio',
                'Memory Optimization Impact',
                'Cache Performance Metrics',
                'System Performance Metrics',
                'Memory Allocation Distribution'
            ),
            vertical_spacing=0.08,
            horizontal_spacing=0.1,
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "sunburst"}]
            ]
        )
        
        # 1. Memory usage over time
        memory_usage = [m['percent'] for m in monitor.memory_history]
        timestamps = [t.strftime('%H:%M:%S') for t in monitor.timestamps]
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=memory_usage,
                name='Memory Usage',
                line=dict(color='#4a90e2', width=2)
            ),
            row=1, col=1
        )
        
        # 2. Cache performance over time
        cache_hits = [c['hits'] for c in monitor.cache_history]
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cache_hits,
                name='Cache Hits',
                line=dict(color='#2ecc71', width=2)
            ),
            row=1, col=2
        )
        
        # 3. Memory usage comparison (if optimization was performed)
        if monitor.optimization_history['memory']['before'] and monitor.optimization_history['memory']['after']:
            memory_comparison = {
                'Before': monitor.optimization_history['memory']['before']['percent'],
                'After': monitor.optimization_history['memory']['after']['percent']
            }
            fig.add_trace(
                go.Bar(
                    x=list(memory_comparison.keys()),
                    y=list(memory_comparison.values()),
                    name='Memory Usage',
                    marker_color=['#ff7675', '#55efc4']
                ),
                row=2, col=1
            )
        
        # 4. Cache hit/miss ratio (current)
        latest_cache = monitor.cache_history[-1] if monitor.cache_history else monitor.get_cache_stats()
        fig.add_trace(
            go.Pie(
                labels=['Hits', 'Misses'],
                values=[latest_cache['hits'], latest_cache['misses']],
                name='Cache Hit/Miss',
                marker=dict(colors=['#00b894', '#ff7675'])
            ),
            row=2, col=2
        )
        
        # 5. Memory optimization impact (if performed)
        if monitor.optimization_history['memory']['before'] and monitor.optimization_history['memory']['after']:
            memory_metrics = {
                'Used': [
                    monitor.optimization_history['memory']['before']['used'] / (1024**3),
                    monitor.optimization_history['memory']['after']['used'] / (1024**3)
                ],
                'Free': [
                    monitor.optimization_history['memory']['before']['free'] / (1024**3),
                    monitor.optimization_history['memory']['after']['free'] / (1024**3)
                ]
            }
            
            fig.add_trace(
                go.Bar(
                    name='Before',
                    x=list(memory_metrics.keys()),
                    y=[memory_metrics[k][0] for k in memory_metrics.keys()],
                    marker_color='#ff7675'
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    name='After',
                    x=list(memory_metrics.keys()),
                    y=[memory_metrics[k][1] for k in memory_metrics.keys()],
                    marker_color='#55efc4'
                ),
                row=3, col=1
            )
        
        # 6. Cache performance metrics (if optimization was performed)
        if monitor.optimization_history['cache']['before'] and monitor.optimization_history['cache']['after']:
            cache_metrics = {
                'Hit Ratio': [
                    monitor.optimization_history['cache']['before']['hit_ratio'] * 100,
                    monitor.optimization_history['cache']['after']['hit_ratio'] * 100
                ],
                'Access Time': [
                    monitor.optimization_history['cache']['before']['access_time'],
                    monitor.optimization_history['cache']['after']['access_time']
                ]
            }
            
            fig.add_trace(
                go.Bar(
                    name='Before',
                    x=list(cache_metrics.keys()),
                    y=[cache_metrics[k][0] for k in cache_metrics.keys()],
                    marker_color='#ff7675'
                ),
                row=3, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    name='After',
                    x=list(cache_metrics.keys()),
                    y=[cache_metrics[k][1] for k in cache_metrics.keys()],
                    marker_color='#55efc4'
                ),
                row=3, col=2
            )

        # 7. System Performance Metrics
        metrics = monitor.performance_metrics
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=metrics['response_times'],
                name='Response Time',
                line=dict(color='#6c5ce7', width=2)
            ),
            row=4, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=metrics['throughput'],
                name='Throughput',
                line=dict(color='#00b894', width=2),
                yaxis='y2'
            ),
            row=4, col=1
        )

        # 8. Memory Allocation Sunburst
        if monitor.memory_history:
            latest_memory = monitor.memory_history[-1]
            total_gb = latest_memory['total'] / (1024**3)
            used_gb = latest_memory['used'] / (1024**3)
            cached_gb = (latest_memory['total'] - latest_memory['available'] - latest_memory['used']) / (1024**3)
            free_gb = latest_memory['free'] / (1024**3)
            
            fig.add_trace(
                go.Sunburst(
                    labels=['Total', 'Used', 'Cached', 'Free', 'Active', 'Inactive'],
                    parents=['', 'Total', 'Total', 'Total', 'Used', 'Used'],
                    values=[total_gb, used_gb, cached_gb, free_gb, used_gb * 0.7, used_gb * 0.3],
                    branchvalues='total',
                    marker=dict(
                        colors=['#2ecc71', '#e74c3c', '#3498db', '#95a5a6', '#e67e22', '#9b59b6']
                    ),
                    name='Memory Distribution'
                ),
                row=4, col=2
            )

        # Update layout for better visualization
        fig.update_layout(
            height=1400,  # Increased height for more charts
            showlegend=True,
            template='plotly_dark',  # Change to dark theme for better contrast
            paper_bgcolor='rgba(45, 52, 54, 1)',  # Dark background
            plot_bgcolor='rgba(45, 52, 54, 1)',  # Dark background 
            font=dict(
                family='Segoe UI, sans-serif',
                size=12,
                color='#dfe6e9'  # Light colored text for dark background
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='#dfe6e9')  # Light colored legend text
            )
        )

        # Add second y-axis for throughput with better colors
        fig.update_layout(
            yaxis7=dict(title=dict(text="Response Time (ms)", font=dict(color='#6c5ce7')), tickfont=dict(color='#dfe6e9')),
            yaxis8=dict(title=dict(text="Throughput (req/s)", font=dict(color='#00b894')), tickfont=dict(color='#dfe6e9'), overlaying="y7", side="right")
        )

        # Update axes labels for all charts with better colors
        fig.update_xaxes(title_text="Time", title_font=dict(color='#dfe6e9'), tickfont=dict(color='#dfe6e9'), row=1, col=1)
        fig.update_xaxes(title_text="Time", title_font=dict(color='#dfe6e9'), tickfont=dict(color='#dfe6e9'), row=1, col=2)
        fig.update_yaxes(title_text="Memory Usage (%)", title_font=dict(color='#4a90e2'), tickfont=dict(color='#dfe6e9'), row=1, col=1)
        fig.update_yaxes(title_text="Cache Hits", title_font=dict(color='#2ecc71'), tickfont=dict(color='#dfe6e9'), row=1, col=2)
        fig.update_yaxes(title_text="Memory Usage (%)", title_font=dict(color='#4a90e2'), tickfont=dict(color='#dfe6e9'), row=2, col=1)
        fig.update_yaxes(title_text="GB", title_font=dict(color='#dfe6e9'), tickfont=dict(color='#dfe6e9'), row=3, col=1)
        fig.update_yaxes(title_text="Value", title_font=dict(color='#dfe6e9'), tickfont=dict(color='#dfe6e9'), row=3, col=2)

        return jsonify(fig.to_dict())
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return jsonify({'error': 'Error generating visualization'}), 500

def compare_performance(before, after):
    """Calculate performance improvement metrics"""
    if before <= 0:
        improvement_percent = 0
    else:
        # For memory usage, lower is better, so improvement is negative change
        # For cache hit ratio, higher is better, so improvement is positive change
        improvement_percent = ((after - before) / before) * 100
    
    return {
        'before_ratio': before,
        'after_ratio': after,
        'improvement': improvement_percent
    }

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Error starting the application: {str(e)}")
