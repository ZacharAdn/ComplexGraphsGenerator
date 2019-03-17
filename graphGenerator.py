import random
import sys
import matplotlib.pyplot as plt
import networkx as nx
import time
import collections

# Usage - python3 graphGenerator.py <num_of_vertices> <max_degree> <seed_number> (optional)<is_weighted>

global_vertices = []
global_in_vertices = []


class Vertex(object):
    def __init__(self, _id, _state, _degree):
        self.id = _id
        self.state = _state
        self.max_degree = _degree
        self.out_degree = 0
        self.in_degree = 0
        self.has_father = False
        self.sons = {}
        self.fathers = {}

    def __str__(self):
        return "vertex: {}, stats: {}, degree: (max-{}, outs-{}, ins-{}), has_father: {}, sons: {}".format(self.id,
                                                                                                           self.state,
                                                                                                           self.max_degree,
                                                                                                           self.out_degree,
                                                                                                           self.in_degree,
                                                                                                           self.has_father,
                                                                                                           self.sons.items)

    def __repr__(self):
        return "<vertex {}>".format(self.id)


def chooseSons(_vertex):
    global need_second_choose

    while _vertex.out_degree < _vertex.max_degree:
        # we are choosing a son that has state of both or in
        curr_son_id = random.choice(global_in_vertices)

        # test if proposal is ok
        while (curr_son_id == _vertex.id) or (curr_son_id in _vertex.sons):
            curr_son_id = random.choice(global_in_vertices)

        if is_weighted:
            weight = random.randint(1, 1000)
        else:
            weight = 1

        _vertex.sons[curr_son_id] = weight
        _vertex.out_degree += 1

        global_vertices[curr_son_id].has_father = True
        global_vertices[curr_son_id].in_degree += 1
        global_vertices[curr_son_id].fathers[_vertex.id] = weight


def main(seed_cmd):
    debug = 0
    plot = 1

    out_filename = 'graphs/edges{}-deg{}-seed{}'.format(num_of_vertices, max_degree, seed_cmd)
    if is_weighted:
        out_filename += '-weighted'
    else:
        out_filename += '-unweighted'

    print("\nStarting generate graph - {}\nStart step 1 (initialize the nodes)".format(out_filename[7:]))

    # initialize the nodes with state and maximum out degree
    seed_init = seed_cmd
    random.seed(seed_init)

    print_count = int(num_of_vertices / 100)

    # the first vertex most be out
    v_state = ['Out']
    for v_id in range(num_of_vertices):
        if v_id % print_count == 0:
            sys.stdout.write('%d \r' % v_id)
            sys.stdout.flush()

        # the last vertex most be in
        if v_id == num_of_vertices - 1:
            v_state = ['In']

        v_degree = random.randint(1, max_degree)
        if debug: print(v_degree)

        v = Vertex(v_id, v_state, v_degree)
        global_vertices.append(v)

        if v_state == ['In'] or v_state == ['Both']:
            global_in_vertices.append(v_id)

        v_state = random.choices(['In', 'Out', 'Both'], [0.2, 0.2, 0.7])
        if debug: print(v_state)

    print("Finish of step 1...\n\nStart step 2 (find a father for every node)")

    # visit all the vertices that can get In edge, and associating a father....
    for i, vertex in enumerate(global_vertices):
        if i % print_count == 0:
            sys.stdout.write('%d \r' % i)
            sys.stdout.flush()

        if vertex.state == ['Out'] or vertex.state == ['Both']:
            # means that node have son or more
            chooseSons(vertex)

    print('Finish of step 2...\n\nStart step 3 (save to file)')

    # save in edges.csv file (GraphSim and Neo4j input)

    with open(out_filename + '.g', 'w') as outFile:
        for i, vertex in enumerate(global_vertices):
            if i % print_count == 0:
                sys.stdout.write('%d \r' % i)
                sys.stdout.flush()

            ordered_sons = collections.OrderedDict(sorted(vertex.sons.items()))
            for son, weight in ordered_sons.items():
                edge = '{},'.format(vertex.id) + '{},'.format(son) + 'T,{}\n'.format(weight)

                # if i == len(vertices)-2 and j == len(vertex.sons)-1:
                # edge = edge[:-1]

                outFile.write(edge)
                # print(edge)

    outFile.close()

    print('Finish of step 3...')

    if debug:
        # print the vertices and their in and out degree
        for v in global_vertices:
            print('\n\n\nVertex id: {}'.format(v.id).ljust(20), 'state: {}'.format(v.state).ljust(10),
                  'Max degree: {}'.format(v.max_degree).ljust(17)
                  , 'Out degree: {}'.format(v.out_degree).ljust(17), 'In degree: {}'.format(v.in_degree).ljust(15),
                  'has_father'.format(v.has_father))

            print('sons:')
            for k, val in v.sons.items():
                print('(son: {}, weight: {})'.format(k, val), end=', ')

            print('\nfathers:')
            for k, val in v.fathers.items():
                print('(father: {}, weight: {})'.format(k, val), end=', ')
        print()

        # print adjacency matrix and prepare network graph
        print('In\Out'.ljust(4), end=' ')
        for i in range(len(global_vertices)):
            print(str(i).ljust(4), end=' ')
        print("\n")

        for vertex in global_vertices:
            print(str(vertex.id).ljust(6), end=' ')
            for _vertex in global_vertices:
                ids = _vertex.sons.keys()
                if _vertex.id in ids:
                    print(str(vertex.sons[ids.index(_vertex.id)]).ljust(4), end=' ')
                else:
                    print(str(0).ljust(4), end=' ')
            print()

    if plot:
        print('\n\nStart step 4 (plotting the graph)')
        # plot network graph
        G = nx.Graph().to_directed()
        for i,vertex in enumerate(global_vertices):
            if i % print_count == 0:
                sys.stdout.write('%d \r' % i)
                sys.stdout.flush()

            for s, w in vertex.sons.items():
                G.add_edge(vertex.id, s, weight=w)

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
    is_weighted = False
    argv = sys.argv[1:]

    num_of_vertices = int(argv[0])
    max_degree = int(argv[1])
    seed_num = (int(argv[2]))

    if len(argv) > 3:
        is_weighted = True

    start = time.time()
    main(seed_num)
    end = time.time()
    print('\nExecution time {} seconds'.format(end - start))
