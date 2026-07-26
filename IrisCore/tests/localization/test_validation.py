import unittest

from tests.localization.testscene import TestScene
from utils.localization.graph import build_scene_graph, connected_components
from utils.localization.validation import validate_components

class TestComponentValidation(unittest.TestCase):

    def test_01_unconstrained_component_warning(self):

        scene = TestScene()

        tag = scene.tag("tag")

        objects, detections = scene.build()

        graph = build_scene_graph(
            objects,
            detections,
        )

        components = connected_components(graph)

        warnings = validate_components(
            components,
            [],
        )

        self.assertEqual(
            len(warnings),
            1,
        )

        self.assertEqual(
            warnings[0].component.members,
            {tag},
        )


    def test_02_rule_component_no_warning(self):

        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(
            tag,
            "x",
            5,
        )

        objects, detections = scene.build()

        graph = build_scene_graph(
            objects,
            detections,
        )

        components = connected_components(graph)

        warnings = validate_components(
            components,
            scene._rules,
        )

        self.assertEqual(
            len(warnings),
            0,
        )


    def test_03_mixed_components(self):

        scene = TestScene()

        cam = scene.camera("cam")
        tag_a = scene.tag("tagA")
        tag_b = scene.tag("tagB")

        scene.observe(
            cam,
            tag_a,
        )

        scene.offset(
            tag_b,
            "x",
            5,
        )

        objects, detections = scene.build()

        graph = build_scene_graph(
            objects,
            detections,
        )

        components = connected_components(graph)

        warnings = validate_components(
            components,
            scene._rules,
        )

        self.assertEqual(
            len(warnings),
            1,
        )

        self.assertEqual(
            warnings[0].component.members,
            {cam, tag_a},
        )

if __name__ == '__main__':
    unittest.main()
