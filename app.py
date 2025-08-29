from flask import Flask, render_template, jsonify, request
import networkx as nx
import pandas as pd
import pickle
import json
from datetime import datetime
import os

app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# For GitHub deployment, we'll use a simpler approach
def create_sample_graph():
    """Create a sample graph for demonstration"""
    G = nx.Graph()
    
    # Sample Marvel data (for demo purposes)
    sample_data = {
        'SPIDER-MAN/PETER PARKER': ['CAPTAIN AMERICA', 'IRON MAN/TONY STARK', 'HULK/DR. ROBERT BRUC'],
        'CAPTAIN AMERICA': ['IRON MAN/TONY STARK', 'THOR/DR. DONALD BLAK', 'BLACK WIDOW/NATASHA'],
        'IRON MAN/TONY STARK': ['WAR MACHINE/JAMES R.', 'SPIDER-MAN/PETER PARKER'],
        'WOLVERINE/LOGAN': ['PROFESSOR X', 'STORM/ORORO MUNROE']
    }
    
    for character, connections in sample_data.items():
        for connection in connections:
            G.add_edge(character, connection)
    
    return G

# Use sample data for GitHub deployment
G = create_sample_graph()

@app.route('/')
def index():
    """Main dashboard page"""
    network_stats = {
        'total_characters': G.number_of_nodes(),
        'total_relationships': G.number_of_edges(),
        'network_density': f"{nx.density(G):.6f}",
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return render_template('index.html', network_stats=network_stats)

@app.route('/api/network-stats')
def network_stats():
    """API for network statistics"""
    return jsonify({
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'status': 'success'
    })

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
