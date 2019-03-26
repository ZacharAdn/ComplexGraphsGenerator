import random
import sys
import matplotlib.pyplot as plt
import networkx as nx
import time
import collections
import os.path

# Usage - python3 graphGenerator.py     -v <num_of_vertices>
#                                       -d <max_degree>
#                                       -s <seed_number>
#                                       -w <is_weighted>                                (optional, default - unweighted)
#                                       -f <graph_format>   [graphsim, neptune, neo4j]  (optional, default - graphsim)

global_vertices = []
global_in_vertices = []
global_ins_only = []


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


def chooseSonFromIns(_vertex):
    in_vertex = random.choice(global_ins_only)

    while global_vertices[in_vertex].has_father:
        in_vertex = random.choice(global_ins_only)

    setEdge(_vertex, in_vertex)
    global_ins_only.remove(in_vertex)


def chooseSons(_vertex):
    while _vertex.out_degree < _vertex.max_degree:
        # we are choosing a son that has state of both or in
        curr_son_id = random.choice(global_in_vertices)

        # test if proposal is ok
        while (curr_son_id == _vertex.id) or (curr_son_id in _vertex.sons):
            curr_son_id = random.choice(global_in_vertices)

        setEdge(_vertex, curr_son_id)


def setEdge(_vertex, curr_son_id):
    weight = random.randint(1, 1000)

    if not is_weighted:
        weight = 1

    _vertex.sons[curr_son_id] = weight
    _vertex.out_degree += 1

    global_vertices[curr_son_id].has_father = True
    global_vertices[curr_son_id].in_degree += 1
    global_vertices[curr_son_id].fathers[_vertex.id] = weight


def main():
    print("\nStarting generate graph - {}\nStart step 1 (initialize the nodes)".format(out_filename[7:]))

    # initialize the nodes with state and maximum out degree
    random.seed(seed_num)
    print_count = int(num_of_vertices / 100)

    # the first vertex most be out
    v_state = Out
    for v_id in range(num_of_vertices):
        if num_of_vertices > 100:
            if v_id % print_count == 0:
                sys.stdout.write('{} ({}%) \r'.format(v_id, int((v_id / num_of_vertices) * 100)))
                sys.stdout.flush()

        # the last vertex most be in
        if v_id == num_of_vertices - 1:
            v_state = In
        v_degree = random.randint(1, max_degree)
        if debug: print(v_degree)

        v = Vertex(v_id, v_state, v_degree)
        global_vertices.append(v)
        if v_state == In:
            global_in_vertices.append(v_id)
            global_ins_only.append(v_id)
        elif v_state == Both:
            global_in_vertices.append(v_id)
        v_state = random.choices(['In', 'Out', 'Both'], [0.1, 0.1, 0.8])
        if debug: print(v_state)

    print(
        'Finish of step 1...\n\nStart step 2 (make sure graph is connected, associating a father for every in vertex)')
    # visit all the vertices that can get In edge, and associating a father....
    while len(global_ins_only) > 0:
        sys.stdout.write('{} in vertices steel not verified as connected.. \r'.format(len(global_ins_only)))
        sys.stdout.flush()
        vertex = random.choice(global_vertices)
        chooseSonFromIns(vertex)

    ins_without_father = 0
    for v_id in global_ins_only:
        if not global_vertices[v_id].has_father:
            ins_without_father += 1
    print('num of in vertices that not has father: {} ({} %)'.format(ins_without_father, (
                (ins_without_father / len(global_vertices)) * 100)))

    print("Finish of step 2...\n\nStart step 3 (find a sons for every out node till max degree)")
    for i, vertex in enumerate(global_vertices):
        if num_of_vertices > 100:
            if i % print_count == 0:
                sys.stdout.write('{} ({}%) \r'.format(i, int((i / num_of_vertices) * 100)))
                sys.stdout.flush()

        if vertex.state == Out or vertex.state == Both:
            # means that node have son or more
            chooseSons(vertex)

    print('Finish of step 3...\n\nStart step 4 (save to file)')
    # save in edges.csv file (GraphSim and Neo4j input)
    with open(out_filename, 'w') as outFile:
        if graph_format == 'neptune':
            outFile.write('~id, ~from, ~to, weight:Double\n')

        for i, vertex in enumerate(global_vertices):
            if num_of_vertices > 100:
                if i % print_count == 0:
                    sys.stdout.write('{} ({}%) \r'.format(i, int((i / num_of_vertices) * 100)))
                    sys.stdout.flush()

            ordered_sons = collections.OrderedDict(sorted(vertex.sons.items()))
            for son, weight in ordered_sons.items():
                edge = '{},'.format(vertex.id) + '{},'.format(son) + 'T,{}\n'.format(weight)
                outFile.write(edge)
    outFile.close()
    print('Finish step 4')

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

        # print adjacency matrix
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
        print('\n\nStart step 5 (plotting the graph')

        # plot network graph
        G = nx.Graph().to_directed()
        for i, vertex in enumerate(global_vertices):
            if i % print_count == 0:
                sys.stdout.write('%d \r' % i)
                sys.stdout.flush()

            for s, w in vertex.sons.items():
                G.add_edge(vertex.id, s, weight=w)

        e = [(u, v) for (u, v, d) in G.edges(data=True)]
        pos = nx.layout.spring_layout(G)
        nx.draw(G, pos)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_nodes(G, pos, node_size=10)
        nx.draw_networkx_edges(G, pos, edgelist=e, width=0.5, arrowstyle='->', arrowsize=4, edge_color='b')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
        plt.show()
        # plt.savefig(<wherever>)


if __name__ == "__main__":
    debug = 0
    plot = 0

    argv = sys.argv[1:]
    is_weighted = False
    graph_format = 'graphsim'
    In, Out, Both = ['In', 'Out', 'Both']

    print(argv)
    for i, arg in enumerate(argv):
        if '-v' == arg:
            num_of_vertices = int(argv[i + 1])
        if '-d' == arg:
            max_degree = int(argv[i + 1])
        if '-s' == arg:
            seed_num = int(argv[i + 1])
        if '-w' == arg:
            is_weighted = True
        if '-f' == arg:
            graph_format = argv[i + 1].lower()
            # 'graphsim' or 'neptune' or 'neo4j'

    out_filename = 'graphs/edges{}-deg{}-seed{}'.format(num_of_vertices, max_degree, seed_num)
    if is_weighted:
        out_filename += '-weighted'
    else:
        out_filename += '-unweighted'

    if graph_format == 'neptune' or graph_format == 'neo4j':
        out_dir = out_filename + '-' + graph_format
        file_suffix = 1
        while os.path.exists(out_dir):
            out_dir = out_filename + '-' + graph_format + '_' + str(file_suffix)
            file_suffix += 1
        out_filename = out_dir
        os.mkdir(out_dir)

        if graph_format == 'neptune':
            vertexFile = open(out_dir + '/vertex.csv', 'w')
            vertexFile.write('~id\n')
            out_filename += ('/edge.csv')

        else:
            nodesHeaderFile = open(out_dir + '/nodes_headers.csv', 'w')
            nodesHeaderFile.write('nodes:ID\n')
            nodesHeaderFile.close()

            edgersHeaderFile = open(out_dir + '/edges_headers.csv', 'w')
            edgersHeaderFile.write(':START_ID,:END_ID,:TYPE,dist:int\n')
            edgersHeaderFile.close()

            vertexFile = open(out_dir + '/nodes.g', 'w')
            out_filename += ('/edges.g')

        vertices_list = range(num_of_vertices)
        for vertex in vertices_list:
            vertexFile.write(str(vertex) + '\n')
        vertexFile.close()

    else:
        out_filename += ('-' + graph_format + '.g')

        tmp_filename = out_filename
        file_suffix = 1
        while os.path.exists(tmp_filename):
            tmp_filename = out_filename[:-2] + '_' + str(file_suffix) + out_filename[-2:]
            file_suffix += 1
        out_filename = tmp_filename

    start = time.time()
    main()
    end = time.time()
    print('\nExecution time {} seconds'.format(end - start))
