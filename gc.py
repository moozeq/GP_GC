#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import List


def error(msg: str):
    print(f'[ERROR] {msg}')
    sys.exit(1)


def download_seq(seq: str) -> str:
    seq_filename = f'{seq}.fasta'
    if Path(seq_filename).exists():
        return seq_filename

    from Bio import Entrez

    Entrez.email = 'A.N.Other@example.com'
    handle = Entrez.efetch(db="nucleotide", id=seq, rettype="fasta", retmode="text")
    record = handle.read()
    with open(seq_filename, 'w') as f:
        f.write(record)
    return seq_filename


def get_seq(seq_filename: str) -> str:
    if not Path(seq_filename).exists():
        error('No sequence file')

    from Bio import SeqIO

    for record in SeqIO.parse(seq_filename, "fasta"):
        return record.seq


def calc_gc_ratio(window_seq: str) -> float:
    return (window_seq.count('G') + window_seq.count('C')) / len(window_seq)


def calc_gc_skew_ratio(window_seq: str) -> float:
    return (window_seq.count('G') - window_seq.count('C')) / (window_seq.count('G') + window_seq.count('C'))


def calc(seq: str, window_size: int, step: int, ratio_func) -> List[float]:
    if len(seq) < window_size:
        error('Wrong window size')
    if window_size < step:
        error('Wrong step')
    if not ratio_func:
        error('Wrong function')

    gc_ratios = []
    cur_pos = window_size
    while cur_pos < len(seq):
        gc_window_ratio = ratio_func(seq[cur_pos - window_size:cur_pos])
        gc_ratios.append(gc_window_ratio)
        cur_pos += step

    return gc_ratios


def gc_plot(gc_ratios: List[float], func_type: str):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(20, 10))
    plt.ylim(ratio_funcs[func_type]["ylim"])
    plt.ylabel(ratio_funcs[func_type]["ylabel"])
    plt.title(f'GC calculations: {ratio_funcs[func_type]["title"]}')

    plt.plot(gc_ratios)
    plt.show()


ratio_funcs = {
    'gc_ratio': {
        'func': calc_gc_ratio,
        'title': 'GC ratio (G+C)/(G+C+A+T)',
        'ylim': (0.0, 1.0),
        'ylabel': 'GC ratio'
    },
    'gc_skew': {
        'func': calc_gc_skew_ratio,
        'title': 'GC skew (G-C)/(G+C)',
        'ylim': (-0.5, 0.5),
        'ylabel': 'GC skew'
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GC calculations')
    parser.add_argument('seq', type=str, help='sequence')
    parser.add_argument('-w', '--window', type=int, default=1000, help='window size')
    parser.add_argument('-s', '--step', type=int, default=10, help='step')
    parser.add_argument('-f', '--func', type=str, choices=ratio_funcs.keys(), default=next(iter(ratio_funcs)), help='ratio function')
    args = parser.parse_args()
    seq_filename = download_seq(args.seq)
    seq = get_seq(seq_filename)
    gc_ratio = calc(seq, args.window, args.step, ratio_funcs[args.func]['func'])
    gc_plot(gc_ratio, args.func)
