// Enhanced visualization settings
const colorScheme = {
    primary: '#a29bfe',
    secondary: '#00ffff',
    accent: '#fd79a8',
    background: 'rgba(45, 52, 54, 0.5)',
    text: '#ffffff'
};

// Improved chart configuration
const chartConfig = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
        format: 'png',
        filename: 'memory_comparison',
        height: 600,
        width: 1200,
        scale: 2
    },
    displaylogo: false
};

// Function to create animated bar charts
function createBarChart(elementId, data) {
    const labels = data.labels || [];
    const values = data.values || [];
    const title = data.title || 'Comparison';
    
    const chartData = [{
        x: labels,
        y: values,
        type: 'bar',
        marker: {
            color: values.map((v, i) => 
                `rgba(108, 92, 231, ${0.5 + (i / values.length * 0.5)})`
            ),
            line: {
                color: colorScheme.secondary,
                width: 1.5
            }
        },
        hoverinfo: 'y+name',
        hovertemplate: '%{y} MB<extra></extra>',
        text: values.map(v => `${v.toFixed(2)} MB`),
        textposition: 'auto',
    }];
    
    const layout = {
        title: {
            text: title,
            font: {
                family: 'Poppins, sans-serif',
                size: 22,
                color: colorScheme.text
            }
        },
        autosize: true,
        height: 500,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 60,
            r: 30,
            t: 80,
            b: 60
        },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            tickfont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            }
        },
        yaxis: {
            title: 'Memory Usage (MB)',
            titlefont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            },
            gridcolor: 'rgba(255,255,255,0.1)',
            tickfont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            }
        },
        animations: [{
            fromcurrent: true,
            transition: {
                duration: 800,
                easing: 'cubic-in-out'
            },
            frame: {
                duration: 800
            }
        }]
    };
    
    // Create the chart with animation
    Plotly.newPlot(elementId, chartData, layout, chartConfig);
}

// Function to create animated line charts
function createLineChart(elementId, data) {
    const x = data.x || [];
    const y = data.y || [];
    const title = data.title || 'Time Series';
    
    const chartData = [{
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: colorScheme.secondary,
            width: 3,
            shape: 'spline',
            smoothing: 1.3
        },
        marker: {
            color: colorScheme.accent,
            size: 8,
            line: {
                color: '#fff',
                width: 2
            }
        },
        hoverinfo: 'y+x',
        hovertemplate: '%{y} MB<extra></extra>'
    }];
    
    const layout = {
        title: {
            text: title,
            font: {
                family: 'Poppins, sans-serif',
                size: 22,
                color: colorScheme.text
            }
        },
        autosize: true,
        height: 500,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 60,
            r: 30,
            t: 80,
            b: 60
        },
        xaxis: {
            title: 'Time',
            titlefont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            },
            gridcolor: 'rgba(255,255,255,0.1)',
            tickfont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            }
        },
        yaxis: {
            title: 'Memory Usage (MB)',
            titlefont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            },
            gridcolor: 'rgba(255,255,255,0.1)',
            tickfont: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            }
        }
    };
    
    Plotly.newPlot(elementId, chartData, layout, chartConfig);
}

// Function to create animated pie charts
function createPieChart(elementId, data) {
    const labels = data.labels || [];
    const values = data.values || [];
    const title = data.title || 'Distribution';
    
    const chartData = [{
        type: 'pie',
        values: values,
        labels: labels,
        textinfo: 'percent',
        insidetextfont: {
            family: 'Poppins, sans-serif',
            color: '#ffffff',
            size: 14
        },
        hoverinfo: 'label+percent+value',
        marker: {
            colors: [
                colorScheme.primary,
                colorScheme.secondary,
                colorScheme.accent,
                '#74b9ff',
                '#55efc4'
            ],
            line: {
                color: '#2d3436',
                width: 2
            }
        }
    }];
    
    const layout = {
        title: {
            text: title,
            font: {
                family: 'Poppins, sans-serif',
                size: 22,
                color: colorScheme.text
            }
        },
        height: 500,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 20,
            r: 20,
            t: 80,
            b: 20
        },
        legend: {
            font: {
                family: 'Poppins, sans-serif',
                color: colorScheme.text
            }
        }
    };
    
    Plotly.newPlot(elementId, chartData, layout, chartConfig);
}

function fetchData() {
    fetch('/api/comparison')
        .then(response => response.json())
        .then(data => {
            document.getElementById("before").textContent = data.before_optimization;
            document.getElementById("after").textContent = data.after_optimization;
        })
        .catch(error => console.error("Error fetching comparison data:", error));
}
