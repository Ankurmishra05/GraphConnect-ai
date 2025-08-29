from flask import Flask, render_template, jsonify
import networkx as nx
import json
from datetime import datetime

app = Flask(__name__)

# Create a sample graph (lightweight for production)
def create_sample_graph():
    """Create a lightweight sample graph for production"""
    G = nx.Graph()
    
    # Sample Marvel data (optimized for production)
    sample_characters = {
        'SPIDER-MAN': ['IRON MAN', 'CAPTAIN AMERICA', 'HULK'],
        'CAPTAIN AMERICA': ['IRON MAN', 'THOR', 'BLACK WIDOW'],
        'IRON MAN': ['WAR MACHINE', 'SPIDER-MAN'],
        'WOLVERINE': ['PROFESSOR X', 'STORM']
    }
    
    for character, connections in sample_characters.items():
        for connection in connections:
            G.add_edge(character, connection)
    
    return G

# Initialize graph
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

@app.route('/api/character/<name>')
def get_character_data(name):
    """API for character data"""
    name_upper = name.upper()
    
    if name_upper not in G:
        return jsonify({'error': 'Character not found'}), 404
    
    return jsonify({
        'name': name_upper,
        'connections': G.degree(name_upper),
        'neighbors': list(G.neighbors(name_upper)),
        'centrality': round(nx.degree_centrality(G).get(name_upper, 0), 6)
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
