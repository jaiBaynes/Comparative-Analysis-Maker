from comparative_visualizer import Visualizer, Comparand, FeatureStatus
import csv
from typing import List, Tuple


def parse_state(token: str) -> FeatureStatus:
    t = token.strip().upper()
    if t in ('2', 'PERFECT', 'P', 'PERF'):
        return FeatureStatus.PERFECT
    if t in ('1', 'PARTIAL', 'PART', 'PA', 'D', 'DISPUTED'):
        return FeatureStatus.PARTIAL
    return FeatureStatus.NONE


def load_from_csv(path: str) -> Tuple[List[str], List[Comparand]]:
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [r for r in reader if any(cell.strip() for cell in r)]
    if not rows:
        return [], []
    header = [c.strip() for c in rows[0] if c.strip()]
    if header and header[0].upper() == 'NEW_COMPARISON':
        features = header[1:]
    else:
        features = header
    comparands: List[Comparand] = []
    for r in rows[1:]:
        if not any(cell.strip() for cell in r):
            continue
        name = r[0].strip()
        states = [parse_state(tok) for tok in r[1:1+len(features)]]
        comparands.append(Comparand(name, states))
    return features, comparands


def load_csv_blocks(path: str) -> List[Tuple[List[str], List[Comparand]]]:
    """Parse multiple comparison blocks from a CSV.

    Blocks are delimited by rows whose first cell equals 'NEW_COMPARISON'
    (case-insensitive). A header row may itself begin with 'NEW_COMPARISON',
    in which case the remainder of that header row lists feature labels.
    Returns a list of (features, comparands) tuples in file order.
    """
    blocks: List[Tuple[List[str], List[Comparand]]] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [r for r in reader if any(cell.strip() for cell in r)]

    i = 0
    n = len(rows)
    while i < n:
        header = [c.strip() for c in rows[i] if c.strip()]
        i += 1
        if not header:
            continue
        if header[0].upper() == 'NEW_COMPARISON':
            features = header[1:]
        else:
            features = header

        comparands: List[Comparand] = []
        while i < n and not (rows[i] and rows[i][0].strip().upper() == 'NEW_COMPARISON'):
            r = rows[i]
            i += 1
            if not any(cell.strip() for cell in r):
                continue
            name = r[0].strip()
            states = [parse_state(tok) for tok in r[1:1+len(features)]]
            comparands.append(Comparand(name, states))

        if features:
            blocks.append((features, comparands))

    return blocks


def load_txt_blocks(path: str) -> List[Tuple[List[str], List[Comparand]]]:
    """Parse multiple comparison blocks from a TXT file using the same
    NEW_COMPARISON header convention as CSV blocks.
    """
    blocks: List[Tuple[List[str], List[Comparand]]] = []
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if l.strip()]

    i = 0
    n = len(lines)
    while i < n:
        header = [c.strip() for c in lines[i].split(',') if c.strip()]
        i += 1
        if not header:
            continue
        if header[0].upper() == 'NEW_COMPARISON':
            features = header[1:]
        else:
            features = header

        comparands: List[Comparand] = []
        while i < n and not (lines[i].split(',')[0].strip().upper() == 'NEW_COMPARISON'):
            line = lines[i]
            i += 1
            if '|' in line:
                name, rest = line.split('|', 1)
                tokens = [t.strip() for t in rest.split(',') if t.strip()]
            else:
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if not parts:
                    continue
                name = parts[0]
                tokens = parts[1:]
            states = [parse_state(tok) for tok in tokens[:len(features)]]
            comparands.append(Comparand(name.strip(), states))

        if features:
            blocks.append((features, comparands))

    return blocks


def load_from_txt(path: str) -> Tuple[List[str], List[Comparand]]:
    features = []
    comparands: List[Comparand] = []
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if l.strip()]
    if not lines:
        return [], []
    header = [c.strip() for c in lines[0].split(',') if c.strip()]
    if header and header[0].upper() == 'NEW_COMPARISON':
        features = header[1:]
    else:
        features = header
    for line in lines[1:]:
        if '|' in line:
            name, rest = line.split('|', 1)
            tokens = [t.strip() for t in rest.split(',') if t.strip()]
        else:
            parts = [p.strip() for p in line.split(',') if p.strip()]
            if not parts:
                continue
            name = parts[0]
            tokens = parts[1:]
        states = [parse_state(tok) for tok in tokens[:len(features)]]
        comparands.append(Comparand(name.strip(), states))
    return features, comparands


def main():
    SOURCE = 'csv'  # 'hardcoded', 'csv', or 'txt'

    demo_features = [
        'king of gods', 'eagle association', 'lustful/seducer', 'cognates', 'fight serpent',
        'storm god powers', 'thunderbolt weapon', 'fight giants', 'fought/overthrew father',
        'shape shifter', 'mountain/top home', 'uncertain/disputed'
    ]

    demo_a = Comparand('JUPITER (Roman)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                           FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                           FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PERFECT,
                                           FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT])

    demo_b = Comparand('THOR / THUNAR (Norse)', [FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PARTIAL,
                                                 FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                                 FeatureStatus.PERFECT, FeatureStatus.PARTIAL, FeatureStatus.NONE,
                                                 FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    demo_c = Comparand('INDRA (Vedic)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PARTIAL,
                                         FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                         FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.NONE,
                                         FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    if SOURCE == 'hardcoded':
        features = demo_features
        left = [demo_a, demo_b, demo_c, demo_c, demo_c, demo_c]
        right = [demo_c, demo_c, demo_c, demo_c, demo_c, demo_c]
    else:
        # support multiple comparison blocks in a single file
        if SOURCE == 'csv':
            blocks = load_csv_blocks('sample_data.csv')
        elif SOURCE == 'txt':
            blocks = load_txt_blocks('sample_data.txt')
        else:
            raise RuntimeError('Unknown SOURCE')

        last_viz = None
        last_left = last_right = last_features = None
        for idx, (features, comps) in enumerate(blocks, start=1):
            half = (len(comps) + 1) // 2
            left = comps[:half]
            right = comps[half:]
            viz = Visualizer(features)
            out = viz.export_image(left, right, title=f' ') #f'Comparison_{idx}')
            print(f'Saved image for block {idx} to', out)
            last_viz = viz
            last_left, last_right, last_features = left, right, features

        # if at least one block was processed, render the last one interactively
        # if last_viz is not None:
        #    last_viz.render_columns(last_left, last_right, title='The Many Other ZEUSes (demo)')


if __name__ == '__main__':
    main()
