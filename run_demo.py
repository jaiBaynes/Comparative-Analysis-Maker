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
    features = [c.strip() for c in rows[0] if c.strip()]
    comparands: List[Comparand] = []
    for r in rows[1:]:
        name = r[0].strip()
        states = [parse_state(tok) for tok in r[1:1+len(features)]]
        comparands.append(Comparand(name, states))
    return features, comparands


def load_from_txt(path: str) -> Tuple[List[str], List[Comparand]]:
    features = []
    comparands: List[Comparand] = []
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if l.strip()]
    if not lines:
        return [], []
    features = [c.strip() for c in lines[0].split(',') if c.strip()]
    for line in lines[1:]:
        if '|' in line:
            name, rest = line.split('|', 1)
            tokens = [t.strip() for t in rest.split(',') if t.strip()]
        else:
            parts = [p.strip() for p in line.split(',') if p.strip()]
            name = parts[0]
            tokens = parts[1:]
        states = [parse_state(tok) for tok in tokens[:len(features)]]
        comparands.append(Comparand(name.strip(), states))
    return features, comparands


def main():
    SOURCE = "hardcoded" # 'csv'  # 'hardcoded', 'csv', or 'txt'

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
        if SOURCE == 'csv':
            features, comps = load_from_csv('sample_data.csv')
        elif SOURCE == 'txt':
            features, comps = load_from_txt('sample_data.txt')
        else:
            raise RuntimeError('Unknown SOURCE')
        half = (len(comps) + 1) // 2
        left = comps[:half]
        right = comps[half:]

    viz = Visualizer(features)
    out = viz.export_image(left, right, title='The Many Other ZEUSes (demo)')
    print('Saved image to', out)
    viz.render_columns(left, right, title='The Many Other ZEUSes (demo)')


if __name__ == '__main__':
    main()
