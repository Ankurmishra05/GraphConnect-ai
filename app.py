from flask import Flask, render_template, jsonify, request
import networkx as nx
import pandas as pd
import pickle
import json
from datetime import datetime

app = Flask(__name__)

# Load pre-processed graph data
def load_graph_data():
    """Load the Marvel graph and pre-computed metrics"""
    try:
        with open('data/marvel_network.pkl', 'rb') as f:
            graph_data = pickle.load(f)
        return graph_data
    except:
        # Fallback: create from scratch (for first run)
        print("Pre-processing graph data...")
        import kagglehub
        import os
        
        dataset_path = kagglehub.dataset_download("csanhueza/the-marvel-universe-social-network")
        edges_file_path = os.path.join(dataset_path, "edges.csv")
        edges_df = pd.read_csv(edges_file_path, header=None, names=['source', 'target'])
        
        G = nx.from_pandas_edgelist(edges_df, source='source', target='target')
        
        # Precompute metrics for performance
        graph_data = {
            'graph': G,
            'degree_centrality': nx.degree_centrality(G),
            'pagerank': nx.pagerank(G),
            'communities': list(nx.community.greedy_modularity_communities(G)),
            'last_updated': datetime.now()
        }
        
        # Save for future use
        with open('data/marvel_network.pkl', 'wb') as f:
            pickle.dump(graph_data, f)
            
        return graph_data

# Load data
graph_data = load_graph_data()
G = graph_data['graph']

@app.route('/')
def index():
    """Main dashboard page"""
    network_stats = {
        'total_characters': G.number_of_nodes(),
        'total_relationships': G.number_of_edges(),
        'network_density': f"{nx.density(G):.6f}",
        'last_updated': graph_data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Top characters for dashboard
    top_chars = sorted(graph_data['degree_centrality'].items(), 
                      key=lambda x: x[1], reverse=True)[:10]
    
    return render_template('index.html', 
                         network_stats=network_stats,
                         top_characters=top_chars)

@app.route('/api/character/<name>')
def get_character_data(name):
    """API endpoint for character data"""
    if name not in G:
        return jsonify({'error': 'Character not found'}), 404
    
    character_data = {
        'name': name,
        'degree_centrality': graph_data['degree_centrality'].get(name, 0),
        'pagerank': graph_data['pagerank'].get(name, 0),
        'connections': G.degree(name),
        'neighbors': list(G.neighbors(name))[:20],  # First 20 neighbors
        'community': next((i for i, comm in enumerate(graph_data['communities']) 
                          if name in comm), -1)
    }
    
    return jsonify(character_data)

@app.route('/api/recommendations/<name>')
def get_recommendations(name):
    """API for connection recommendations"""
    from networkx.algorithms import link_prediction
    
    if name not in G:
        return jsonify({'error': 'Character not found'}), 404
    
    recommendations = []
    for other_char in list(G.nodes())[:100]:  # Sample for performance
        if other_char != name and not G.has_edge(name, other_char):
            try:
                score = list(link_prediction.resource_allocation_index(
                    G, [(name, other_char)]))[0][2]
                recommendations.append({'character': other_char, 'score': score})
            except:
                continue
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(recommendations[:10])

@app.route('/api/network-stats')
def network_stats():
    """API for network statistics"""
    return jsonify({
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes()
    })

@app.route('/character/<name>')
def character_detail(name):
    """Character detail page"""
    return render_template('character.html', character_name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
