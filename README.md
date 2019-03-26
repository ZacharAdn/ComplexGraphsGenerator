# graphGenerator

## Fraud graph generator for graph databases

Generate directed, connected, weighted (or not..) graph files for 'GraphSim', 'Neo4j' and Amazons - 'Neptune' graph database platforms<br><br>
Enable controlling on the graph size, maximum out degree of a vertex in the graph, weights type and out format <br> 
Plot an network graph using 'networkx' and debugging options allowed

<pre>
Usage - python3 graphGenerator.py     -v (num_of_vertices)
                                      -d (max_degree)
                                      -s (seed_number)
                                      -w (boolean - is_weighted)                                (optional, default - unweighted)
                                      -f (graph_format)   [graphsim, neptune, neo4j]   (optional, default - graphsim)


Usage example:
[zachara@ip-xxx-xx-xx-xxx]$ python3 graphGenerator.py -v 1048576 -d 16 -s 5 -w -f graphsim
</pre>