from flask import Flask, render_template, jsonify
import networkx as nx
from datetime import datetime

app = Flask(__name__)

# Lightweight sample data for production
def create_marvel_graph():
    G = nx.Graph()
    
    # Core Marvel characters and connections
    characters = {
        'SPIDER-MAN': ['IRON MAN', 'CAPTAIN AMERICA', 'HULK', 'BLACK WIDOW'],
        'CAPTAIN AMERICA': ['IRON MAN', 'THOR', 'BLACK WIDOW', 'HAWKEYE'],
        'IRON MAN': ['WAR MACHINE', 'SPIDER-MAN', 'CAPTAIN AMERICA'],
        'WOLVERINE': ['PROFESSOR X', 'STORM', 'CYCLOPS'],
        'THOR': ['CAPTAIN AMERICA', 'LOKI', 'HEIMDALL']
    }
    
    for character, connections in characters.items():
        for connection in connections:
            G.add_edge(character, connection)
    
    return G

G = create_marvel_graph()

@app.route('/')
def home():
    stats = {
        'total_characters': G.number_of_nodes(),
        'total_relationships': G.number_of_edges(), 
        'network_density': f"{nx.density(G):.6f}",
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return render_template('index.html', network_stats=stats)

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'status': 'success'
    })

@app.route('/api/character/<name>')
def character_api(name):
    name_upper = name.upper().replace('-', ' ')
    
    if name_upper not in G:
        return jsonify({'error': 'Character not found. Try: SPIDER-MAN, CAPTAIN AMERICA, IRON MAN'}), 404
    
    return jsonify({
        'name': name_upper,
        'connections': G.degree(name_upper),
        'centrality': round(nx.degree_centrality(G).get(name_upper, 0), 4),
        'neighbors': list(G.neighbors(name_upper))
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
