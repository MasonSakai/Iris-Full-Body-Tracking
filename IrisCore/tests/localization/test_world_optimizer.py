import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from tests.localization.testscene import TestScene
from utils.localization.graph import Graph
from utils.localization.objects import SolverIdent
from utils.localization.optimizer import ConstraintAnalysis

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

    def assertConstraint(
        self,
        analysis: ConstraintAnalysis,
        rank: int,
        dof: int,
    ):
        self.assertEqual(
            analysis.total_rank,
            rank,
        )
        self.assertEqual(
            analysis.total_dof,
            dof,
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

        scene.offset(tag, 'x', 5)
        scene.offset(tag, 'y', 2)
        scene.offset(tag, 'z', 3)

        _, _, _, poses = scene.solve_scene()
        
        np.testing.assert_allclose(
            poses[tag][:3,3],
            [5, 2, 3],
            atol=1e-6,
        )

    def test_02_facing_rule(self):
        scene = TestScene()

        cam = scene.camera("cam")
        tag = scene.tag("tag")

        scene.observe(cam, tag)

        scene.facing(tag, [1,0,0])

        _, _, _, poses = scene.solve_scene()

        self.assertFacing(
            poses[tag],
            [1,0,0],
        )

    def test_03_rule_only_object_world_solve(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(tag, "x", 5)
        scene.offset(tag, "y", 2)
        scene.offset(tag, "z", 3)

        graph, relative, world, poses = scene.solve_scene()

        self.assertIn(tag, poses)

        np.testing.assert_allclose(
            poses[tag][:3,3],
            [5,2,3],
            atol=1e-5,
        )

    def test_04_detected_and_rule_only_components(self):
        scene = TestScene()

        cam = scene.camera("cam")
        tag_a = scene.tag("tagA")
        tag_b = scene.tag("tagB")

        scene.observe(cam, tag_a)

        scene.offset(tag_b, "x", 5)
        scene.offset(tag_b, "y", 2)
        scene.offset(tag_b, "z", 3)
        
        graph, relative, world, poses = scene.solve_scene()
        
        self.assertIn(tag_a, poses)
        self.assertIn(tag_b, poses)

        np.testing.assert_allclose(
            poses[tag_b][:3,3],
            [5,2,3],
            atol=1e-5,
        )

    def test_05_multiple_world_components(self):

        scene = TestScene()

        cam_a = scene.camera("camA")
        tag_a = scene.tag("tagA")

        cam_b = scene.camera("camB")
        tag_b = scene.tag("tagB")

        scene.observe(cam_a, tag_a)
        scene.observe(cam_b, tag_b)

        scene.offset(tag_a, "x", 5)
        scene.offset(tag_a, "y", 2)
        scene.offset(tag_a, "z", 1)

        scene.offset(tag_b, "x", -3)
        scene.offset(tag_b, "y", 4)
        scene.offset(tag_b, "z", 2)

        graph, relative, world, poses = scene.solve_scene()

        self.assertEqual(
            len(relative),
            2,
        )

        np.testing.assert_allclose(
            poses[tag_a][:3,3],
            [5,2,1],
            atol=1e-5,
        )

        np.testing.assert_allclose(
            poses[tag_b][:3,3],
            [-3,4,2],
            atol=1e-5,
        )

    def test_06_conflicting_offset_rules_have_cost(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(tag, "x", 1)
        scene.offset(tag, "x", 5)

        graph, relative, world, poses = scene.solve_scene()

        self.assertGreater(
            world.final_cost,
            0,
        )

        # The least-squares solution should be halfway between them
        np.testing.assert_allclose(
            poses[tag][:3,3],
            [3,0,0],
            atol=1e-5,
        )

    def test_07_constraints_offset_xyz(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(tag, "x", 1)
        scene.offset(tag, "y", 2)
        scene.offset(tag, "z", 3)

        _, _, world, poses = scene.solve_scene()

        analysis = world.constraint_analysis[0]

        self.assertConstraint(
            analysis,
            rank=3,
            dof=3,
        )

    def test_08_constraints_facing(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.facing(
            tag,
            [1,0,0],
        )

        _, _, world, poses = scene.solve_scene()

        analysis = world.constraint_analysis[0]

        self.assertConstraint(
            analysis,
            rank=2,
            dof=4,
        )

    def test_09_constraints_offset_and_facing(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(tag, "x", 1)
        scene.offset(tag, "y", 2)
        scene.offset(tag, "z", 3)

        scene.facing(
            tag,
            [1,0,0],
        )

        _, _, world, poses = scene.solve_scene()

        analysis = world.constraint_analysis[0]

        self.assertConstraint(
            analysis,
            rank=5,
            dof=1,
        )

    def test_10_duplicate_constraints_do_not_add_rank(self):
        scene = TestScene()

        tag = scene.tag("tag")

        scene.offset(tag, "x", 1)
        scene.offset(tag, "x", 5)
        scene.offset(tag, "x", 10)

        _, _, world, poses = scene.solve_scene()

        analysis = world.constraint_analysis[0]

        self.assertConstraint(
            analysis,
            rank=1,
            dof=5,
        )

    def test_11_constraints_are_per_component(self):
        scene = TestScene()

        tag_a = scene.tag("tagA")
        tag_b = scene.tag("tagB")

        scene.offset(tag_a, "x", 1)
        scene.offset(tag_a, "y", 2)
        scene.offset(tag_a, "z", 3)

        scene.offset(tag_b, "x", 4)
        scene.offset(tag_b, "y", 5)
        scene.offset(tag_b, "z", 6)

        _, _, world, poses = scene.solve_scene()

        self.assertEqual(
            len(world.constraint_analysis),
            2,
        )

        for analysis in world.constraint_analysis.values():
            self.assertConstraint(
                analysis,
                rank=3,
                dof=3,
            )

    def test_12_unconstrained_component(self):
        scene = TestScene()

        tag = scene.tag("tag")

        _, _, world, poses = scene.solve_scene()

        analysis = world.constraint_analysis[0]

        self.assertConstraint(
            analysis,
            rank=0,
            dof=6,
        )
        self.assertEqual(world.iterations, 0)
        self.assertEqual(world.final_cost, 0)

if __name__ == '__main__':
    unittest.main()

