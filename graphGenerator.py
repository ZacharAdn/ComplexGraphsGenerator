import random
import sys
from random import choices
import matplotlib.pyplot as plt
import networkx as nx


class Vertex(object):
    def __init__(self, _id, _state, _degree):
        self.id = _id
        self.state = _state
        self.max_degree = _degree
        self.out_degree = 0
        self.in_degree = 0
        self.visited = False
        self.sons = []

    def __str__(self):
        return "vertex: {}, stats: {}, degree: (max-{}, outs-{}, ins-{}), visited: {}, sons: {}".format(self.id, self.state, self.max_degree, self.out_degree, self.in_degree, self.visited, self.sons)

    def __repr__(self):
        return "<vertex {}>".format(self.id)


def chooseNeighbor(_neighbors, _vertex):
    if len(_neighbors) < 1:
        return

    curr_neighbor = random.choice(_neighbors)
    if (curr_neighbor.state == ['Out']) or (curr_neighbor.id in [v[0].id for v in _vertex.sons]) or (curr_neighbor.id == _vertex.id):
        _neighbors.remove(curr_neighbor)

        curr_neighbor = chooseNeighbor(_neighbors, _vertex)

    return curr_neighbor


def genEdge(vertex, neighbor, vertices):
    if is_weighted:
        weight = random.randint(1, 1000)
    else:
        weight = 1

    vertex.sons.append([neighbor, weight])
    vertices[vertices.index(neighbor)].in_degree += 1
    vertices[vertices.index(neighbor)].visited = True
    vertex.out_degree += 1


def main():
    vertices = []

    states = ['In', 'Out', 'Both']
    prob = [0.2, 0.2, 0.7]

    # initialize the nodes with state and maximum out degree
    v_state = ['Out']
    for v_id in range(num_of_vertices):
        if v_id == num_of_vertices-1:
            v_state = ['In']

        v_degree = random.randint(1, max_degree)

        v = Vertex(v_id, v_state, v_degree)
        vertices.append(v)
        v_state = choices(states, prob)

    # visit all the vertices that can get In edge
    neighbors = list(vertices)
    for vertex in vertices:
        if vertex.state != ['In']:
            neighbor = chooseNeighbor(neighbors, vertex)
            if neighbor is not None:
                genEdge(vertex, neighbor, vertices)
                neighbors.remove(neighbor)

    # fill the vertices with sons till max_degree or end of neighbors
    for vertex in vertices:
        if vertex.state != ['In']:
            while vertex.out_degree == 0 or vertex.out_degree < vertex.max_degree:
                neighbors = list(vertices)
                neighbors.remove(vertex)
                neighbor = chooseNeighbor(neighbors, vertex)
                if neighbor is not None:
                    genEdge(vertex, neighbor, vertices)
                else:
                    break

    # save in edges.csv file (GraphSim and Neo4j input)
    with open('edges{}.csv'.format(num_of_vertices), 'w') as outFile:
        for vertex in vertices:
            for son in vertex.sons:
                edge = '{},'.format(vertex.id).ljust(4) + '{},'.format(son[0].id).ljust(4) + 'T, {}\n'.format(son[1])
                print(edge)
                outFile.write(edge)

    # print the vertices and their in and out degree
    for v in vertices:
        print('Vertex id: {}'.format(v.id).ljust(20), 'Out degree: {}'.format(v.out_degree).ljust(17),
              'In degree: {}'.format(v.in_degree).ljust(15))
    print()

    # print adjacency matrix and prepare network graph
    print('In\Out'.ljust(4), end=' ')
    for i in range(len(vertices)):
        print(str(i).ljust(4), end=' ')
    print("\n")

    G = nx.Graph().to_directed()
    for vertex in vertices:
        for son in vertex.sons:
            G.add_edge(vertex.id, son[0].id, weight=son[1])

        print(str(vertex.id).ljust(6), end=' ')
        for _vertex in vertices:
            ids = [v[0].id for v in vertex.sons]
            if _vertex.id in ids:
                print(str(vertex.sons[ids.index(_vertex.id)][1]).ljust(4), end=' ')
            else:
                print(str(0).ljust(4), end=' ')
        print()

    # plot network graph
    e = [(u, v) for (u, v, d) in G.edges(data=True)]
    pos = nx.layout.random_layout(G)
    nx.draw(G, pos)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_nodes(G, pos, node_size=10)
    nx.draw_networkx_edges(G, pos, edgelist=e, width=0.5, arrowstyle='->', arrowsize=4, edge_color='b')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    plt.show()
    # plt.savefig(<wherever>)


if __name__ == "__main__":
    argv = sys.argv[1:]

    num_of_vertices = int(argv[0])
    max_degree = int(argv[1])
    is_weighted = True
    if len(argv) > 2:
        is_weighted = False

    main()