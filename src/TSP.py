import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt


def haversine(coord1, coord2):
    # Tính khoảng cách theo đơn vị km
    R = 6371  # Bán kính Trái Đất
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return R * c

def compute_distance_matrix(locations):
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine(locations[i], locations[j])
            matrix[i][j] = matrix[j][i] = dist
    return matrix


def generate_random_route(n_cities):
    route = list(range(1, n_cities))
    random.shuffle(route)
    return [0] + route

def compute_route_distance(route, distances):
    total = 0
    for i in range(len(route) - 1):
        total += distances[route[i]][route[i + 1]]
    total += distances[route[-1]][route[0]]  # Quay về điểm đầu
    return total

def visualize(locations, route, title='Best Route'):
    G = nx.Graph()
    for i, (lat, lon) in enumerate(locations):
        G.add_node(i, pos=(lon, lat))  # Note: lon = x, lat = y

    edges = [(route[i], route[i + 1]) for i in range(len(route) - 1)]
    if route[-1] != route[0]:
        edges.append((route[-1], route[0]))  # chỉ nối nếu điểm cuối khác điểm đầu
    G.add_edges_from(edges)

    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, node_color='skyblue', node_size=500, with_labels=True, font_size=9)
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='r', width=2)
    plt.title(title)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()