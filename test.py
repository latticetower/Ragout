#!/usr/bin/env python

import sys
from collections import namedtuple, defaultdict

Entry = namedtuple("Entry", ["s_ref", "e_ref", "s_qry", "e_qry", "len_ref", "len_qry", "contig_id"])
Scaffold = namedtuple("Scaffold", ["name", "contigs"])

def parse_quast_output(filename):
    entries = []
    for line in open(filename, "r"):
        if line.startswith(" ") or line.startswith("="):
            continue

        vals = line.strip("\n").split(" | ")
        coord_ref = map(int, vals[0].split(" "))
        coord_qry = map(int, vals[1].split(" "))
        lengths = map(int, vals[2].split(" "))
        cname = vals[4].split(" ")[1]
        entries.append(Entry( *(coord_ref + coord_qry + lengths + [cname]) ))

    return entries


def parse_contigs_order(filename):
    scaffolds = []
    for line in open(filename, "r"):
        if line.startswith(">"):
            scaffolds.append(Scaffold(line.strip()[1:], []))
        else:
            if line.startswith("gaps"):
                pass
            else:
                name = line.strip("\n").replace("=", "_") #fix for quast
                scaffolds[-1].contigs.append(name)
    return scaffolds


def main():
    entries = parse_quast_output(sys.argv[1])

    by_name = defaultdict(list)
    for entry in entries:
        by_name[entry.contig_id].append(entry)
    for name in by_name:
        by_name[name].sort(key=lambda e: e.len_qry, reverse=True)
        #print map(lambda e: e.len_qry, by_name[name])
    filtered = [e[0] for e in by_name.itervalues()]

    by_start = sorted(filtered, key=lambda e: e.s_ref)
    ordered = map(lambda e: e.contig_id, by_start)

    scaffolds = parse_contigs_order(sys.argv[2])
    zero_step = False
    for s in scaffolds:
        order = map(lambda c: ordered.index(c), s.contigs)

        #check order
        fail = False
        print s.name, order
        for i, num in enumerate(order):
            if i == 0:
                prev = num
            elif i == 1:
                increasing = num > prev
                prev = num
            else:
                if (num > prev) != increasing:
                    if not zero_step and abs(num - prev) > max(order) / 2:
                        zero_step = True
                        print "zero step"
                    else:
                        print ("fail between {0} ({1}) and {2} ({3})"
                                .format(s.contigs[i - 1], prev, s.contigs[i], num))
                        fail = True
                prev = num

        if not fail:
            print "ok"


if __name__ == "__main__":
    main()
