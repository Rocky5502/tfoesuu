#!/usr/bin/env python3
"""Enumerate small fairness graphs to stress-test the T3 fractional-cover hypothesis.

This script does not establish a theorem. It finds graph structures where a
fractional replay allocation differs from integral edge coverage, giving proof
targets and potential counterexamples.
"""
from __future__ import annotations
import argparse, json
import networkx as nx

from tfoesuu.graph_replay import fractional_vertex_cover, integral_vertex_cover_size
from tfoesuu.graphs import from_edges


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-n",type=int,default=7)
    ap.add_argument("--top",type=int,default=25)
    args=ap.parse_args()
    rows=[]
    # NetworkX graph atlas contains every unlabeled graph up to 7 vertices.
    for g in nx.graph_atlas_g():
        n=g.number_of_nodes()
        if n<2 or n>args.max_n or g.number_of_edges()==0:
            continue
        h=from_edges(n,tuple(g.edges()),family="atlas")
        frac=fractional_vertex_cover(h)
        integ=integral_vertex_cover_size(h)
        ratio=integ/frac.objective
        rows.append({
            "n":n,"m":h.m,"edges":[list(e) for e in h.edges],
            "fractional_cover":frac.objective,
            "integral_cover":integ,
            "integrality_ratio":ratio,
            "bipartite":nx.is_bipartite(g),
        })
    rows.sort(key=lambda r:(-r["integrality_ratio"],r["n"],r["m"]))
    print(json.dumps({
        "status":"COMPUTATIONAL_THEOREM_SEARCH_ONLY",
        "graphs_checked":len(rows),
        "top_integrality_gaps":rows[:args.top],
    },indent=2))

if __name__=="__main__":
    main()
