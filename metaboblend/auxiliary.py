#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2019-2020 Jack Gisby, Ralf Weber
#
# This file is part of MetaboBlend.
#
# MetaboBlend is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MetaboBlend is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MetaboBlend.  If not, see <https://www.gnu.org/licenses/>.
#

import itertools
import pylab as plt
import networkx as nx


def calculate_complete_multipartite_graphs(max_atoms_available, max_n_substructures):
    """
    Calculates all possible configurations of multipartite graphs up to (inclusive) a given number of atoms available
    and number of substructures. The possible bonding configurations for these graphs are
    calculated by geng and RI, before they are used to combine substructures and generate novel metabolites.

    :param max_n_substructures: The maximal number of substructures (vertices). At least two substructures must be
        available for bonding for a graph to be created.

    :param max_atoms_available: The maximal number of atoms available (maximal number of edges per vertex) in each
        substructure for bonding. At least one atom must be available for bonding for a graph to be created.

    :return: A string detailing each possible combination of atoms_available and n_substructures (p) and the
        complete multipartite :py:meth:`networkx.Graph` generated from these parameters (g).
    """

    if isinstance(max_atoms_available, list):
        sizes = max_atoms_available
    elif isinstance(max_atoms_available, int):
        sizes = [i + 1 for i in range(max_atoms_available)]

    for nb in range(2, max_n_substructures+1):
        for p in itertools.combinations_with_replacement(sizes, nb):
            g = nx.complete_multipartite_graph(*p)
            yield g, p


def get_degrees(max_atoms_available, ug):
    """
    Calculate the degree (number of atoms available for bonding) for each substructure (node) in a given connectivity
    graph configuration.

    :param max_atoms_available: The maximal atoms available in each substructure for bonding. At least one
        atom must be available for bonding for a graph to be created.

    :param ug: A :py:meth:`networkx.Graph` generated by geng and labelled using the mappings calculated by RI.

    :return: The degree available for each substructure in the graph as a tuple of tuples.
    """

    num = 0
    temp = [0]
    for s in max_atoms_available:
        num += s
        temp.append(num)

    degrees_nodes = ()
    for i in range(len(temp)-1):
        degree_nodes_sub = [t[1] for t in ug.degree(range(temp[i], temp[i + 1]))]
        degrees_nodes += (tuple(degree_nodes_sub),)

    return degrees_nodes


def draw_subgraph(edges, vn):
    """
    Generates a visual representation of a connectivity subgraph, generated by geng and labelled using the mappings
    provided by RI.

    :param edges: Tuple containing tuple of integers representing edges of the connectivity subgraph.

    :param vn: String containing the degrees (number of atoms available for bonding) of the subgraph's substructures
        (nodes), as generated by :py:meth:`metaboblend.auxiliary.get_degrees`.

    :return: A tuple containing :py:meth:`pylab.plt` and :py:meth:`networkx.Graph` objects based on the connectivity
        subgraph.
    """

    plt.title(str(vn))

    s_g = nx.Graph()
    s_g.add_edges_from([(e[0], e[1]) for e in edges])

    pos = nx.circular_layout(s_g)
    nx.draw(s_g, pos)

    cols = ["b", "r", "g", "y"]
    c_d = {}

    i = 0
    for j, substructure in enumerate(vn):
        if len(substructure) == 1:
            c_d[(i,)] = cols[j]
            i += 1

        elif len(substructure) == 2:
            c_d[(i, i + 1)] = cols[j]
            i += 2

    for k in c_d.keys():
        nx.draw_networkx_nodes(s_g, pos=pos, nodelist=k, node_color=c_d[k], node_size=800, alpha=1.0)

    nx.draw_networkx_labels(s_g, pos=pos)

    return plt, s_g


def graph_to_ri(graph: nx.Graph, name):
    """
    Converts a :py:meth:`networkx.Graph` to gfu format to be read by RI. Allows for calculation of mappings by RI which
    relate the output of geng to the complete multipartite graphs generated by
    :py:meth:`metaboblend.auxiliary.calculate_complete_multipartite_graphs`.

    :param graph: Graph generated by networkx (e.g. one generated by
        :py:meth:`metaboblend.auxiliary.calculate_complete_multipartite_graphs` or geng).

    :param name: String containing the graph's name for identification.

    :return: String containing the graph in gfu (undirected graphs with attributes only on nodes) format.
    """

    out = "#{}\n".format(name)
    out += "{}\n".format(graph.number_of_nodes())

    for n in graph.nodes():
        out += "n\n"

    out += "{}\n".format(graph.number_of_edges())

    for e in graph.edges():
        out += "{} {} e\n".format(e[0], e[1])

    return out


def graph_info(p, s_g, mappings):
    """
    Generates and sorts valence and edge information.

    :param p: String containing a connectivity subgraph configuration generated by
        :py:meth:`metaboblend.auxiliary.calculate_complete_multipartite_graphs`.

    :param s_g: A :py:meth:`networkx.Graph` connectivity subgraph generated by geng based on the output of
        :py:meth:`metaboblend.auxiliary.calculate_complete_multipartite_graphs`.

    :param mappings: Mappings calculated by RI for the relabelling of a subgraph generated by geng. Used by get_valences
        in order to calculate bond degrees.

    :return: A dictionary whose keys contain substructure valences and objects that are list of lists containing the
        possible sets of edges between the substructures specified by the key.
    """

    frags = {}

    for m in mappings:
        ug = nx.relabel_nodes(s_g, m, copy=True)
        vn = get_degrees(p, ug)

        e = list(ug.edges())
        e.sort()

        if str(vn) not in frags:
            frags[str(vn)] = [e]
        else:
            if e not in frags[str(vn)]:
                frags[str(vn)].append(e)

    return frags


def sort_subgraphs(subgraphs):
    """
    Sorts a lists of edges for a given connectivity subgraph, provided by :py:meth:`metaboblend.auxiliary.graph_info`,
    to allow duplicate sets of edges to be removed; the order of the edges is sorted for each substructure (node)
    before the order of the substructures is sorted, so that all non-unique subgraphs are identical.

    :param subgraphs: A list of lists containing a tuple of the possible sets of edges between substructures in a
        connectivity graph, created by :py:meth:`metaboblend.auxiliary.graph_info`.

    :return: The same list of subgraphs given as input, ordered by both the tuple of edges for each substructure in the
        subgraphs and the list of these tuples.
    """

    sorted_subgraphs = set()

    for fr in subgraphs:
        sorted_subgraphs.add(tuple(sorted([tuple(sorted(e)) for e in fr])))

    return [list(fr) for fr in sorted_subgraphs]
