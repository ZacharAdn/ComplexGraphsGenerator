# graphGenerator

## Fraud graph generator for graph databases

Generate directed, connected, weighted (or not..) graph files for 'GraphSim', 'Neo4j' and Amazons - 'Neptune' graph database platforms<br><br>
Enable controlling graph size, maximum out degree of a vertex in the graph, weights type and output format <br> 
Plot an network graph using 'networkx' and debugging options allowed

<pre>
Usage - python3 graphGenerator.py     -v (integer - num of vertices)
                                      -d (integer - max degree)
                                      -s (integer - seed num)
                                      -w (boolean - is weighted?)                               (optional, default - unweighted)
                                      -f (string  - graph format [graphsim, neptune, neo4j])    (optional, default - graphsim)


Usage example:
[zachara@ip-xxx-xx-xx-xxx]$ python3 graphGenerator.py -v 1048576 -d 16 -s 5 -w -f graphsim
</pre>