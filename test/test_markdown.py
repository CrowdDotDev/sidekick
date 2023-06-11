# -*- coding: utf-8 -*-


def test_parse():
    from sidekick.sources.local import markdown
    chunks = markdown.parse('res/test/local/butterfly-biology.md')

    assert chunks == [
        'Butterflies > Anatomy of a Butterfly > Wings\n\n'
        'Butterflies are known for their large, colorful wings. '
        'The wings are made up of thin layers of chitin, the same '
        'protein that makes up the exoskeleton of a butterfly. '
        'The colors of the wings are created by the reflection and '
        'refraction of light by the microscopic scales that cover them.',

        'Butterflies > Anatomy of a Butterfly > Body\n\n'
        'The body of a butterfly is divided into three parts: the head, '
        'the thorax, and the abdomen. The head houses the eyes, antennae, '
        'and proboscis. The thorax contains the muscles that control the wings. '
        'The abdomen contains the digestive and reproductive organs.',

        'Butterflies > Life Cycle of a Butterfly\n\n'
        'The butterfly has a most interesting life cycle.',

        'Butterflies > Life Cycle of a Butterfly > Caterpillar Stage\n\n'
        'The life cycle of a butterfly begins as an egg. From the egg hatches '
        'the caterpillar, or larva. The caterpillar spends most of its time eating, '
        'growing rapidly and shedding its skin several times.',

        'Butterflies > Life Cycle of a Butterfly > Chrysalis Stage\n\n'
        'Once the caterpillar has grown enough, it forms a chrysalis, or pupa. '
        'Inside the chrysalis, the caterpillar undergoes a transformation '
        'called metamorphosis. Over the course of a few weeks, it reorganizes '
        'its body and emerges as a butterfly.'
    ]
