import numpy as np
from typing import List, Tuple, Optional

class BaselineAnalyzer:
    """
    Baseline analysis for water droplet images.
    Supports two methods:
        - Double Points: Based on two user-selected points.
        - Mirror Image Method: (under development) based on symmetrical images.
    """

    @staticmethod
    def compute_baseline_double_points(points: List[Tuple[float, float]]) -> Optional[Tuple[float, float, float]]:
        """
        Calculate baseline from two points.
        Args:
            Points: List of points (x, y) at least 2 points required.
        Returns:
            (a, b, c) with the equation of the line ax + by + c = 0,
            or None if there are not enough points.
        """
        if len(points) < 2:
            return None

        # Take the first two points
        (x1, y1), (x2, y2) = points[0], points[1]

        # Direction vector
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return None  # two coincident points

        # Equation of a straight line in the form ax + by + c = 0
        a = dy
        b = -dx
        c = dx * y1 - dy * x1

        return (a, b, c)

    @staticmethod
    def compute_baseline_mirror_image(image_array: np.ndarray) -> Optional[Tuple[float, float, float]]:
        """
        Calculate baseline using Mirror Image method
        Currently returns None and will be updated later.
        """
        # TODO: Implement mirror image algorithm
        return None