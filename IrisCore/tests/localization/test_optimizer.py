import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from tests.localization.testscene import TestScene
from utils.localization.graph import Graph, connected_components, from_detections
from utils.localization.objects import SolverIdent
from utils.localization.optimizer import optimize_relative

class TestRelativeOptimizer(unittest.TestCase):

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def assertPoseAlmostEqual(self, expected, actual, atol=1e-6):
        np.testing.assert_allclose(
            expected[:3, 3],
            actual[:3, 3],
            atol=atol,
        )
        np.testing.assert_allclose(
            expected[:3, :3],
            actual[:3, :3],
            atol=atol,
        )

    def assertRelativePose(self, graph, expected, a, b):
        expected_tf = np.linalg.inv(expected[a]) @ expected[b]
        actual_tf = np.linalg.inv(graph[a].relative_pose) @ graph[b].relative_pose

        self.assertPoseAlmostEqual(
            expected_tf,
            actual_tf,
        )

    def perturb_graph(
        self,
        graph: Graph,
        root: SolverIdent,
        translation_sigma=0.05,
        rotation_sigma_deg=5.0,
    ):
        rng = np.random.default_rng(12345)

        for ident, node in graph.items():

            if ident == root:
                continue

            pose = node.relative_pose.copy()

            pose[:3, 3] += rng.normal(
                0,
                translation_sigma,
                3,
            )

            rot = Rotation.from_matrix(
                pose[:3, :3]
            )

            noise = Rotation.from_rotvec(
                np.deg2rad(rotation_sigma_deg)
                * rng.normal(size=3)
            )

            pose[:3, :3] = (
                noise * rot
            ).as_matrix()

            node.relative_pose = pose

    # ------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------

    def test_01_perfect_scene(self):

        scene = TestScene()

        cam = scene.camera("cam")
        tag = scene.tag("tag", scene.T((1, 2, 3)))

        scene.observe(cam, tag)

        graph, traversal = scene.solve_graph()

        scene.optimize_relative(
            graph,
            traversal,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            cam,
            tag,
        )

    def test_02_translation_noise(self):

        scene = TestScene()

        cam = scene.camera("cam")
        tag = scene.tag("tag", scene.T((1, 2, 3)))

        scene.observe(cam, tag)

        graph, traversal = scene.solve_graph()

        self.perturb_graph(
            graph,
            traversal.components[0].root,
            translation_sigma=0.25,
            rotation_sigma_deg=0,
        )

        scene.optimize_relative(
            graph,
            traversal,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            cam,
            tag,
        )

    def test_03_rotation_noise(self):

        scene = TestScene()

        cam = scene.camera("cam")
        tag = scene.tag(
            "tag",
            scene.T(
                (1, 2, 3),
                (15, 20, 30),
            ),
        )

        scene.observe(cam, tag)

        graph, traversal = scene.solve_graph()

        self.perturb_graph(
            graph,
            traversal.components[0].root,
            translation_sigma=0,
            rotation_sigma_deg=20,
        )

        scene.optimize_relative(
            graph,
            traversal,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            cam,
            tag,
        )

    def test_04_combined_noise(self):

        scene = TestScene()

        camA = scene.camera("camA")
        camB = scene.camera(
            "camB",
            scene.T((2, 0, 0)),
        )

        tag = scene.tag(
            "tag",
            scene.T(
                (1, 1, 0),
                (0, 30, 0),
            ),
        )

        scene.observe(camA, tag)
        scene.observe(camB, tag)

        graph, traversal = scene.solve_graph()

        self.perturb_graph(
            graph,
            traversal.components[0].root,
            translation_sigma=0.10,
            rotation_sigma_deg=10,
        )

        scene.optimize_relative(
            graph,
            traversal,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camA,
            tag,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camB,
            tag,
        )

    def test_05_diamond_graph(self):

        scene = TestScene()

        camA = scene.camera(
            "camA",
            scene.T((0, 0, 0)),
        )

        camB = scene.camera(
            "camB",
            scene.T((4, 0, 0)),
        )

        tag1 = scene.tag(
            "tag1",
            scene.T((1, 0, 0)),
        )

        tag2 = scene.tag(
            "tag2",
            scene.T((3, 0, 0)),
        )

        scene.observe_all(camA, tag1, tag2)
        scene.observe_all(camB, tag1, tag2)

        graph, traversal = scene.solve_graph()

        self.perturb_graph(
            graph,
            traversal.components[0].root,
            translation_sigma=0.15,
            rotation_sigma_deg=8,
        )

        scene.optimize_relative(
            graph,
            traversal,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camA,
            tag1,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camA,
            tag2,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camB,
            tag1,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camB,
            tag2,
        )


if __name__ == '__main__':
    unittest.main()

