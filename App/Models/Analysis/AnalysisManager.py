########################################################
# @file App/Models/Analysis/AnalysisManager.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
########################################################
import numpy as np
from typing import List, Tuple, Optional
from App.Models.Analysis.BaselineAnalysis import BaselineAnalyzer
from App.Models.Analysis.DropletAnalysis import (
    EllipsoidFitter,
    YoungLaplaceFitter,
    compute_contact_angle_from_ellipse,
    compute_contact_angle_from_circle
)

class AnalysisManager:
    """
    Manage the entire baseline and droplet analysis process.  
    Major improvements:
    - Weighted Least Squares support for ellipse fit
    - Use Fitzgibbon Direct Ellipse Fit for optimal initialization
    - Pass baseline_coeffs to EllipsoidFitter to calculate weights
    """
    def __init__(self):
        self.analyzer = BaselineAnalyzer()
        self.baseline_coeffs = None

    def compute_baseline(self, method: str, points: List[Tuple[float, float]] = None,
                         image: np.ndarray = None) -> Optional[Tuple[float, float, float]]:
        """
        The baseline is calculated based on the chosen method.
        
        Args:
            method: "Double Points" or "Mirror Image Method"
            points: List of points (x, y) used for Double Points
            image: NumPy array images are used for image mirroring
            
        Returns:
            (a, b, c) Or None if it cannot be calculated
        """
        if method == "Double Points":
            if points is None or len(points) < 2:
                return None
            self.baseline_coeffs = self.analyzer.compute_baseline_double_points(points)
            return self.baseline_coeffs

        elif method == "Mirror Image Method":
            self.baseline_coeffs = self.analyzer.compute_baseline_mirror_image(image)
            return self.baseline_coeffs

        return None

    def is_mirror_method_available(self) -> bool:
        """Check if the Mirror Image method is ready."""
        return False

    def analyze_droplet(self, method: str, baseline_coeffs: Tuple[float, float, float],
                        points: List[Tuple[float, float]]) -> Optional[dict]:
        """
        Droplet analysis is based on the chosen fit method.
        
        Args:
            method: "Ellipsoid Fit" or "Young-Laplace Fit"
            baseline_coeffs: (a,b,c) of baseline
            points: List of points on the droplet boundary (user-selectable)
        
        Returns:
            The dictionary contains the contact angle results (see DropletAnalysis)
        
        Features:
            - Ellipsoid fitters use baseline weights to calculate Weighted Least Squares 
            - Points closer to the baseline have higher weights
        """
        if len(points) < 3:
            return None

        if method == "Ellipsoid Fit":
            # Pass baseline_coeffs to support Weighted Least Squares
            fit_result = EllipsoidFitter.fit(points, baseline_coeffs)
            if fit_result and fit_result['success']:
                return compute_contact_angle_from_ellipse(fit_result, baseline_coeffs)
        
        elif method == "Young-Laplace Fit":
            fit_result = YoungLaplaceFitter.fit(points)
            if fit_result and fit_result['success']:
                return compute_contact_angle_from_circle(fit_result, baseline_coeffs)

        return None

    def get_baseline_coeffs(self) -> Optional[Tuple[float, float, float]]:
        """Return the current baseline coefficient."""
        return self.baseline_coeffs