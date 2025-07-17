# Memory and Cache Optimizer

A comprehensive system utility for memory and cache monitoring and optimization, available both as a desktop application and a web interface.

## Features

- Real-time memory usage monitoring and optimization
- Cache performance tracking and optimization
- Designed specifically for Windows systems
- Detailed before/after optimization comparisons
- Performance metrics tracking

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

Run the launcher script to choose your preferred interface:

```bash
python launcher.py
```

This will present a menu where you can select either the desktop application or web interface.

## Usage - Choose Your Interface

This application offers two interface options:

### Option 1: Desktop Application

The desktop application provides a native UI with real-time monitoring and optimization capabilities.

```bash
python desktop_app.py
```

For full optimization capabilities, run with administrator privileges:
- Right-click and select "Run as administrator"

**Advantages:**
- Native UI performance
- No browser required
- More responsive interface
- Better integration with system

### Option 2: Web Interface

The web interface allows you to access the tool from any browser.

```bash
python run.py
```

Then open your web browser and navigate to:
```
http://localhost:5000
```

**Advantages:**
- Access from any device on your network
- No dependencies on desktop libraries
- May work better on systems without PyQt support

## Feature Details

### Real-time Monitoring
- Memory usage statistics (total, used, free, available)
- Swap usage tracking
- Cache performance metrics (hit/miss ratio, access time)
- System performance indicators

### Optimization
- Memory optimization with real system commands
- Cache optimization including browser cache clearing
- Before/after comparison with visual representation
- Optimization history tracking

### Visualizations
- Memory usage over time graphs
- Cache performance trends
- Before/after optimization comparisons

## System Requirements

- Windows 10/11
- Python 3.7+
- For desktop interface: PyQt5
- For web interface: Modern web browser
- Administrator privileges for full optimization capabilities

## Note on Administrator Privileges

Some optimization features require administrator privileges:
- Memory page file optimization
- System cache clearing
- DNS cache flushing

Without admin privileges, the application will still function but with limited optimization capabilities.
