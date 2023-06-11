# -*- coding: utf-8 -*-


def test_orgmode_parse():
    from sidekick.sources.local import orgmode
    chunks = orgmode.parse('res/test/local/org/trees.org')

    assert chunks == [
        'Trees\n\nTrees are perennial plants with an elongated stem, or trunk, '
        'supporting branches and leaves in most species. They are a vital part '
        'of our ecosystem and provide numerous benefits. This document will '
        'describe a few notable ones.',

        'Trees > Oak Tree > Overview\n\nThe Oak tree, belonging to the genus Quercus, '
        'is known for its strength and longevity. There are about 600 species of oaks, '
        'and they are native to the northern hemisphere.',

        'Trees > Oak Tree > Characteristics\n\nOak trees are large and deciduous, '
        'though a few tropical species are evergreen. They have spirally arranged '
        'leaves and acorns as fruit. The wood of oak trees is notably strong and '
        'durable.',

        'Trees > Maple Tree > Overview\n\nMaple trees are part of the genus Acer. '
        'They are known for their distinctive leaf shape and the production of '
        'maple syrup.',

        'Trees > Maple Tree > Characteristics\n\nMaple trees have a diverse range '
        'of properties, with sizes ranging from shrubs to large trees. The leaves '
        'are usually palmately veined and lobed. The fruit is a double samara with '
        'one wing longer than the other.',

        'Trees > Pine Tree > Overview\n\nPine trees are evergreen, coniferous '
        'resinous trees in the genus Pinus. They are known for their distinctive '
        'pine cones and are often associated with Christmas.',

        'Trees > Pine Tree > Characteristics\n\nPine trees can be identified by '
        'their needle-like leaves, which are bundled in clusters of 2-5. '
        'The bark of most pines is thick and scaly, but some species have thin, '
        'flaky bark.',

        'Trees > Willow Tree > Overview\n\nWillow trees, part of the genus Salix, '
        'are known for their flexibility and their association with water and wetlands.',

        'Trees > Willow Tree > Characteristics\n\nWillow trees are usually '
        'fast-growing but relatively short-lived. They have slender branches and large, '
        'fibrous, often stoloniferous roots. The leaves are typically elongated, '
        'but may also be round to oval.'
    ]
