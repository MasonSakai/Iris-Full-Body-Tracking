import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from tests.localization.testscene import TestScene
from utils.localization.graph import Graph
from utils.localization.objects import SolverIdent
from utils.localization.optimizer import pack_variables
from utils.localization.placement_rules import PlacementRule_Facing, PlacementRule_Offset

class TestWorldOptimizer(unittest.TestCase):

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

    def assertFacing(self, pose, expected):
        actual = pose[:3,:3] @ np.array([0,0,1], dtype=np.float64)
        actual /= np.linalg.norm(actual)

        expected = np.asarray(expected, dtype=np.float64)
        expected /= np.linalg.norm(expected)

        np.testing.assert_allclose(
            actual,
            expected,
            atol=1e-5,
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

    def test_01_world_translation_from_offset(self):

        scene = TestScene()

        cam = scene.camera(
            "cam",
            scene.T((0,0,0)),
        )

        tag = scene.tag(
            "tag",
            scene.T((1,0,0)),
        )

        scene.observe(cam, tag)

        rules = [
            PlacementRule_Offset({
                'weight': 1,
                'target': tag,
                'axis': "x",
                'distance': 5
            }),
            PlacementRule_Offset({
                'weight': 1,
                'target': tag,
                'axis': "y",
                'distance': 2
            }),
            PlacementRule_Offset({
                'weight': 1,
                'target': tag,
                'axis': "z",
                'distance': 3
            }),
        ]

        graph, traversal, result, poses = scene.solve_world(rules)
        
        np.testing.assert_allclose(
            poses[tag][:3,3],
            [5, 2, 3],
            atol=1e-6,
        )

    def test_02_facing_rule(self):
        scene = TestScene()

        cam = scene.camera("cam")

        tag = scene.tag(
            "tag",
            scene.T((0,0,0))
        )

        scene.observe(cam, tag)

        rule = PlacementRule_Facing({
            'target': tag,
            'weight': 1,
            'direction': [1,0,0],
        })

        _, _, _, poses = scene.solve_world([rule])

        self.assertFacing(
            poses[tag],
            [1,0,0],
        )


if __name__ == '__main__':
    unittest.main()

