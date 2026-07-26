import unittest

import numpy as np

from tests.localization.testscene import TestScene
from utils.localization.graph import Graph, connected_components, from_detections
from utils.localization.objects import SolverIdent

class TestGraphSolver(unittest.TestCase):

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def assertPoseAlmostEqual(self, expected: np.ndarray, actual: np.ndarray, atol=1e-6):
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

    def assertRelativePose(
        self,
        graph: Graph,
        expected: dict[SolverIdent, np.ndarray],
        a: SolverIdent,
        b: SolverIdent,
    ):
        """
        Compare the relative transform between two objects.

        expected is a dict of world poses.
        """

        expected_tf = np.linalg.inv(expected[a]) @ expected[b]
        actual_tf = np.linalg.inv(graph[a].relative_pose) @ graph[b].relative_pose

        self.assertPoseAlmostEqual(
            expected_tf,
            actual_tf,
        )

    # ---------------------------------------------------------------------
    # Graph construction
    # ---------------------------------------------------------------------

    def test_01_graph_single_detection(self):

        scene = TestScene()

        cam = scene.camera("camA", scene.T((0, 0, 0)))
        tag = scene.tag("tag", scene.T((1, 2, 3)))

        scene.observe(cam, tag)

        objects, detections = scene.build()

        graph = from_detections(detections)

        self.assertEqual(len(graph), 2)

        self.assertEqual(len(graph[cam].edges), 1)
        self.assertEqual(len(graph[tag].edges), 1)

        self.assertPoseAlmostEqual(
            graph[cam].edges[0].transform,
            scene.T((1, 2, 3)),
        )

        self.assertPoseAlmostEqual(
            graph[tag].edges[0].transform,
            np.linalg.inv(scene.T((1, 2, 3))),
        )

    # ---------------------------------------------------------------------
    # Connected components
    # ---------------------------------------------------------------------

    def test_02_connected_components(self):
        
        scene = TestScene()

        camA = scene.camera("camA", scene.T((0, 0, 0)))
        camB = scene.camera("camB", scene.T((5, 0, 0)))

        tagA = scene.tag("tagA", scene.T((1, 0, 0)))
        tagB = scene.tag("tagB", scene.T((6, 0, 0)))

        scene.observe(camA, tagA)
        scene.observe(camB, tagB)

        objects, detections = scene.build()

        graph = from_detections(detections)

        components = connected_components(graph)

        self.assertEqual(len(components), 2)

        self.assertSetEqual(
            components[0] | components[1],
            {camA, tagA, camB, tagB},
        )

    # ---------------------------------------------------------------------
    # Propagation
    # ---------------------------------------------------------------------

    def test_03_chain_propagation(self):

        scene = TestScene()

        camA = scene.camera("camA", scene.T((0, 0, 0)))
        camB = scene.camera("camB", scene.T((-1, 0, 0)))

        tag = scene.tag("tag", scene.T((1, 0, 0)))

        scene.observe(camA, tag)
        scene.observe(camB, tag)

        graph, result = scene.solve_graph()

        self.assertRelativePose(
            graph,
            scene.poses,
            camA,
            tag,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            camA,
            camB,
        )

        self.assertRelativePose(
            graph,
            scene.poses,
            tag,
            camB,
        )

    # ---------------------------------------------------------------------
    # Multiple estimates
    # ---------------------------------------------------------------------

    def test_04_diamond_generates_two_estimates(self):

        scene = TestScene()

        camA = scene.camera("camA", scene.T((0, 0, 0)))
        camB = scene.camera("camB", scene.T((4, 0, 0)))

        tag1 = scene.tag("tag1", scene.T((1, 0, 0)))
        tag2 = scene.tag("tag2", scene.T((3, 0, 0)))

        scene.observe(camA, tag1)
        scene.observe(camA, tag2)
        scene.observe(camB, tag1)
        scene.observe(camB, tag2)
        
        graph, result = scene.solve_graph()

        est0 = graph[tag2].estimates[0].pose
        est1 = graph[tag2].estimates[1].pose

        self.assertPoseAlmostEqual(
            est0,
            est1,
        )

    # ---------------------------------------------------------------------
    # Rotation
    # ---------------------------------------------------------------------

    def test_05_rotation_propagation(self):

        scene = TestScene()

        cam = scene.camera("cam", scene.T((0, 0, 0)))
        tag = scene.tag("tag", scene.T(rot=(0, 90, 0)))

        scene.observe(cam, tag)

        graph, result = scene.solve_graph()

        self.assertRelativePose(
            graph,
            scene.poses,
            cam,
            tag,
        )


if __name__ == '__main__':
    unittest.main()
