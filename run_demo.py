from comparative_visualizer import Visualizer, Comparand, FeatureStatus


def main():
    features = [
        'Indo-European','king of gods', 'eagle association', 'lustful/seducer', 'cognates', 'fight serpent',
        'storm god powers', 'thunderbolt weapon', 'fight giants', 'fought/overthrew father',
        'shape shifter', 'mountain/top home'
    ]

    viz = Visualizer(features)

    a = Comparand('JUPITER (Roman)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT])

    b = Comparand('THOR / THUNAR (Norse)', [FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PARTIAL,
                                            FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                            FeatureStatus.PERFECT, FeatureStatus.PARTIAL, FeatureStatus.NONE,
                                            FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    c = Comparand('INDRA (Vedic)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PARTIAL,
                                    FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                    FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.NONE,
                                    FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    left = [a, b]
    right = [c]

    out = viz.export_image(left, right, title='The Many Other ZEUSes (demo)')
    print('Saved image to', out)

    viz.render_columns(left, right, title='The Many Other ZEUSes (demo)')


if __name__ == '__main__':
    main()
