import numpy as np
import cv2
from scipy.optimize import least_squares
from scipy.linalg import eig
from typing import Dict, List, Optional, Sequence, Tuple

# ========================================================================
# SOLUTION 1: FITZGIBBON DIRECT ELLIPSE FIT (Optimal Initialization)
# ========================================================================

class FitzgibbonEllipseFitter:
    """
    Implement Fitzgibbon et al. (1999) Direct Ellipse Fit.

    Solves the eigenvalue problem on the general quadratic equation:
        A*x² + B*x*y + C*y² + D*x + E*y + F = 0

    To obtain the optimal ellipse parameters in a single linear computation step.
    """

    @staticmethod
    def fit(points: List[Tuple[float, float]]) -> Optional[Dict]:
        """
        Fitzgibbon Direct Ellipse Fit.

        Args:
            points: List of points (x, y) on the ellipse boundary.

        Returns:
            Dict containing {x0, y0, a, b, theta, success} if successful.
            Or None if failed (insufficient points, singular matrix, etc).
        """
        if len(points) < 5:
            return None

        points_array = np.array(points, dtype=np.float64)
        x = points_array[:, 0]
        y = points_array[:, 1]

        # Construct design matrix D (n x 6)
        # Each row: [x², xy, y², x, y, 1]
        D = np.column_stack([x**2, x*y, y**2, x, y, np.ones_like(x)])

        # Matrix S₁ (6x6): D^T @ D
        S1 = D.T @ D

        # Matrix S₂ (6x6): constraint matrix for ellipse
        # Constraint: 4AC - B² > 0 (ellipse condition, not hyperbola)
        # Vector order: [A, B, C, D, E, F]
        S2 = np.array([
            [0,  0, -2,  0,  0,  0],
            [0,  1,  0,  0,  0,  0],
            [-2, 0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0]
        ], dtype=np.float64)

        try:
            # Solve generalized eigenvalue problem: S₁v = λS₂v
            eigenvalues, eigenvectors = eig(S1, S2)

            # Take the eigenvector corresponding to the smallest (positive) eigenvalue
            # and satisfying the ellipse condition (4AC - B² > 0)
            valid_idx = []
            for i, lam in enumerate(eigenvalues):
                if np.isreal(lam) and np.isfinite(lam):
                    v = eigenvectors[:, i].real
                    A, B, C, D, E, F = v
                    # Check ellipse condition
                    discriminant = 4 * A * C - B**2
                    if discriminant > 1e-6:  # Ellipse condition
                        valid_idx.append(i)

            if not valid_idx:
                return None

            # Take the eigenvector with the smallest eigenvalue among valid eigenvectors
            valid_idx = np.array(valid_idx)
            valid_eigs = eigenvalues[valid_idx].real
            min_valid_idx = valid_idx[np.argmin(np.abs(valid_eigs))]

            v = eigenvectors[:, min_valid_idx].real
            A, B, C, D, E, F = v

            # Normalize so that A + C = 1 (for easier comparison)
            norm = A + C
            if abs(norm) < 1e-10:
                return None
            A, B, C, D, E, F = A / norm, B / norm, C / norm, D / norm, E / norm, F / norm

            # Convert from general equation to canonical form (x0, y0, a, b, theta)
            result = FitzgibbonEllipseFitter._conic_to_ellipse(A, B, C, D, E, F)

            if result is None:
                return None

            x0, y0, a, b, theta = result

            # Ensure a >= b (semi-major >= semi-minor)
            if a < b:
                a, b = b, a
                theta += np.pi / 2

            # Normalize theta to [-π/2, π/2]
            theta = theta % np.pi
            if theta > np.pi / 2:
                theta -= np.pi

            return {
                'x0': float(x0),
                'y0': float(y0),
                'a': float(a),
                'b': float(b),
                'theta': float(theta),
                'success': True
            }

        except Exception as e:
            print(f"Fitzgibbon fit error: {e}")
            return None

    @staticmethod
    def _conic_to_ellipse(A, B, C, D, E, F):
        """
        Convert from general conic equation:
            A*x² + B*x*y + C*y² + D*x + E*y + F = 0

        To canonical ellipse form:
            ((x-x0)*cosθ + (y-y0)*sinθ)²/a² + (-(x-x0)*sinθ + (y-y0)*cosθ)²/b² = 1

        Returns:
            (x0, y0, a, b, theta) or None if failed.
        """
        try:
            # Step 1: Find center (x0, y0) by solving system:
            # 2A*x0 + B*y0 + D = 0
            # B*x0 + 2C*y0 + E = 0

            denom = 4 * A * C - B**2
            if abs(denom) < 1e-10:
                return None

            x0 = (B * E - 2 * C * D) / denom
            y0 = (B * D - 2 * A * E) / denom

            # Step 2: Compute coefficients after translating origin
            # F' = A*x0² + B*x0*y0 + C*y0² + D*x0 + E*y0 + F
            F_prime = A * x0**2 + B * x0 * y0 + C * y0**2 + D * x0 + E * y0 + F

            # Step 3: Find rotation angle θ from geometric matrix
            # Compute eigenvalues of [[A, B/2], [B/2, C]] to find a, b

            if abs(B) < 1e-10:
                # Special case: no rotation or 90° rotation
                if A < C:
                    a_sq = -F_prime / A
                    b_sq = -F_prime / C
                    theta = 0.0
                else:
                    a_sq = -F_prime / C
                    b_sq = -F_prime / A
                    theta = np.pi / 2
            else:
                # Find eigenvalues of [[A, B/2], [B/2, C]]
                trace = A + C
                det = A * C - (B / 2)**2

                lambda1 = (trace + np.sqrt(trace**2 - 4 * det)) / 2
                lambda2 = (trace - np.sqrt(trace**2 - 4 * det)) / 2

                # Semi-axes
                if lambda1 > 1e-10 and lambda2 > 1e-10:
                    a_sq = -F_prime / lambda1
                    b_sq = -F_prime / lambda2
                else:
                    return None

                if abs(B) > 1e-10:
                    theta = 0.5 * np.arctan2(B, A - C)
                else:
                    theta = 0.0

            if a_sq < 1e-10 or b_sq < 1e-10:
                return None

            a = np.sqrt(a_sq)
            b = np.sqrt(b_sq)

            return (float(x0), float(y0), float(a), float(b), float(theta))

        except Exception as e:
            print(f"Conic to ellipse error: {e}")
            return None


# ========================================================================
# SOLUTION 2: ELLIPSOID FITTER WITH FITZGIBBON + WEIGHTED LEAST SQUARES
# ========================================================================

class EllipsoidFitter:
    """
    Fit rotated ellipse (5 parameters) to a set of points.

    Initialization: Use Fitzgibbon Direct Ellipse Fit (optimal in one step)
    Refinement: Weighted Least Squares (high weights near baseline)

    Equation:
        ((x-x0)*cosθ + (y-y0)*sinθ)²/a² + (-(x-x0)*sinθ + (y-y0)*cosθ)²/b² = 1
    
    [FIXED v2.2]
    - Increased alpha from 10.0 to 25.0 to give more weight to points near baseline
    - Improves contact angle accuracy for obtuse angles
    """

    @staticmethod
    def _ellipse_residuals(params, x, y, weights=None):
        """
        Compute scale-aware ellipse residuals.

        Important fix:
        - Use a normalized algebraic / Sampson-like residual instead of the raw conic value.
        - This is much closer to geometric point-to-ellipse distance, so the fitted tangent near
          the contact line is significantly more reliable.
        """
        x0, y0, a, b, theta = params
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        dx = x - x0
        dy = y - y0
        u = dx * cos_t + dy * sin_t
        v = -dx * sin_t + dy * cos_t

        f_val = (u / a) ** 2 + (v / b) ** 2 - 1.0

        # Gradient of the implicit ellipse equation in world coordinates.
        gx = 2.0 * (u * cos_t / (a ** 2) - v * sin_t / (b ** 2))
        gy = 2.0 * (u * sin_t / (a ** 2) + v * cos_t / (b ** 2))
        grad_norm = np.sqrt(gx ** 2 + gy ** 2)

        residuals = f_val / np.maximum(grad_norm, 1e-12)

        if weights is not None:
            residuals = residuals * np.sqrt(weights)

        return residuals

    @staticmethod
    def _compute_weights(x, y, baseline_coeffs: Tuple[float, float, float],
                        alpha: float = 8.0) -> np.ndarray:
        """
        Compute adaptive weights based on distance to baseline.

        Important fix:
        - The original formula used raw physical distance directly in exp(-alpha*d^2).
        - That makes the weighting depend strongly on image scale / calibration.
        - Here distances are normalized by a robust characteristic scale of the droplet,
          so the fit behaviour is stable across different resolutions and unit systems.
        """
        a_line, b_line, c_line = baseline_coeffs

        numerator = np.abs(a_line * x + b_line * y + c_line)
        denominator = np.sqrt(a_line**2 + b_line**2)

        if denominator < 1e-10:
            return np.ones_like(x)

        distance = numerator / denominator
        scale = np.percentile(distance, 75)
        scale = max(scale, np.max(distance) * 0.25, 1e-6)
        normalized_distance = distance / scale

        weights = np.exp(-alpha * normalized_distance**2)
        return np.clip(weights, 1e-4, 1.0)

    @staticmethod
    def fit(points: List[Tuple[float, float]],
            baseline_coeffs: Tuple[float, float, float] = None) -> Optional[Dict]:
        """
        Fit ellipse using Fitzgibbon + Weighted Least Squares.

        Args:
            points: List of points (x, y) on the ellipse boundary
            baseline_coeffs: (a, b, c) of baseline (for computing weights).
                           If None, all weights = 1.

        Returns:
            Dict {x0, y0, a, b, theta, success} if successful, None if failed.
        """
        if len(points) < 5:
            return None

        x = np.array([p[0] for p in points], dtype=np.float64)
        y = np.array([p[1] for p in points], dtype=np.float64)

        # ===== STEP 1: Fitzgibbon Direct Ellipse Fit (initialization) =====
        fitzgibbon_result = FitzgibbonEllipseFitter.fit(points)
        if fitzgibbon_result is None:
            x0_init = np.mean(x)
            y0_init = np.mean(y)
            a_init = (np.max(x) - np.min(x)) / 2
            b_init = (np.max(y) - np.min(y)) / 2
            theta_init = 0.0
        else:
            x0_init = fitzgibbon_result['x0']
            y0_init = fitzgibbon_result['y0']
            a_init = fitzgibbon_result['a']
            b_init = fitzgibbon_result['b']
            theta_init = fitzgibbon_result['theta']

        # ===== STEP 2: Compute weights based on baseline =====
        if baseline_coeffs is not None:
            weights = EllipsoidFitter._compute_weights(x, y, baseline_coeffs, alpha=25.0)
        else:
            weights = np.ones_like(x)

        # ===== STEP 3: Weighted Least Squares Refinement =====
        try:
            result = least_squares(
                EllipsoidFitter._ellipse_residuals,
                [x0_init, y0_init, a_init, b_init, theta_init],
                args=(x, y, weights),
                bounds=(
                    [-np.inf, -np.inf, 1e-6, 1e-6, -np.pi / 2],
                    [ np.inf,  np.inf, np.inf, np.inf,  np.pi / 2]
                ),
                loss='soft_l1',
                f_scale=0.02,
                max_nfev=8000
            )

            if result.success:
                x0, y0, a, b, theta = result.x

                if a < b:
                    a, b = b, a
                    theta += np.pi / 2

                theta = theta % np.pi
                if theta > np.pi / 2:
                    theta -= np.pi

                return {
                    'x0': float(x0),
                    'y0': float(y0),
                    'a': float(a),
                    'b': float(b),
                    'theta': float(theta),
                    'success': True
                }
        except Exception as e:
            print(f"Least squares fit error: {e}")

        return None


# ========================================================================
# YOUNG-LAPLACE FITTER (Kept unchanged)
# ========================================================================

class YoungLaplaceFitter:
    """
    Simplified version: fit circle (approximation for small droplets, neglecting gravity).
    Equation: (x - x0)^2 + (y - y0)^2 = R^2
    """

    @staticmethod
    def _circle_residuals(params, x, y):
        """Use geometric radial residual instead of squared-radius algebraic residual."""
        x0, y0, R = params
        radial_distance = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        return radial_distance - R

    @staticmethod
    def fit(points: List[Tuple[float, float]]) -> Optional[Dict]:
        if len(points) < 3:
            return None
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        x0_init = np.mean(x)
        y0_init = np.mean(y)
        R_init = np.mean(np.sqrt((x - x0_init) ** 2 + (y - y0_init) ** 2))
        try:
            result = least_squares(
                YoungLaplaceFitter._circle_residuals,
                [x0_init, y0_init, R_init],
                args=(x, y),
                bounds=([-np.inf, -np.inf, 1e-6], np.inf)
            )
            if result.success:
                x0, y0, R = result.x
                return {
                    'x0': x0,
                    'y0': y0,
                    'R': R,
                    'success': True
                }
        except Exception:
            pass
        return None


# ========================================================================
# HELPER FUNCTIONS FOR ROBUST "INSIDE-LIQUID" CONTACT ANGLE
# ========================================================================

def _normalize_vector(v: Tuple[float, float], eps: float = 1e-12) -> Optional[np.ndarray]:
    """Normalize a 2D vector to unit length."""
    v = np.asarray(v, dtype=np.float64)
    n = np.hypot(v[0], v[1])
    if n < eps:
        return None
    return v / n


def _angle_deg_between(v1: Tuple[float, float], v2: Tuple[float, float]) -> Optional[float]:
    """Compute angle between two vectors in degrees, clamped to [0, 180]."""
    u1 = _normalize_vector(v1)
    u2 = _normalize_vector(v2)
    if u1 is None or u2 is None:
        return None
    dot = np.clip(np.dot(u1, u2), -1.0, 1.0)
    return float(np.degrees(np.arccos(dot)))


def _point_side_relative_to_baseline(pt: Tuple[float, float], baseline_coeffs: Tuple[float, float, float]) -> float:
    """Signed line evaluation ax + by + c."""
    a, b, c = baseline_coeffs
    return a * pt[0] + b * pt[1] + c


def _sign_with_tolerance(value: float, tol: float = 1e-10) -> int:
    """Stable sign helper with tolerance."""
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def _oriented_baseline_inside_direction(
    contact_pt: Tuple[float, float],
    baseline_coeffs: Tuple[float, float, float],
    footprint_midpoint: Tuple[float, float]
) -> Optional[np.ndarray]:
    """
    Baseline direction oriented from the contact point toward the wetted footprint.
    This is the correct substrate direction for the inside-liquid contact angle.
    """
    a_line, b_line, _ = baseline_coeffs
    baseline_dir = _normalize_vector((b_line, -a_line))
    if baseline_dir is None:
        return None

    to_mid = np.asarray(footprint_midpoint, dtype=np.float64) - np.asarray(contact_pt, dtype=np.float64)
    if np.dot(baseline_dir, to_mid) < 0:
        baseline_dir = -baseline_dir
    return baseline_dir


def _select_tangent_using_curve_branch(
    contact_t: float,
    point_fn,
    derivative_fn,
    baseline_coeffs: Tuple[float, float, float],
    inside_sign: int,
    reference_pt: Tuple[float, float],
    step: float = 1e-4
) -> Optional[np.ndarray]:
    """
    Select the tangent orientation by following the *actual parametric curve branch*
    (t + step) or (t - step), rather than taking a tiny step along the tangent line.

    Why this matters:
    - A step along the tangent line is not guaranteed to stay on the liquid interface.
    - Near obtuse angles, that can flip the tangent to the wrong branch and produce
      theta vs (180 - theta) mistakes.

    The chosen direction is the branch whose neighbouring curve point lies deeper on the
    liquid side of the baseline. If both are numerically ambiguous, use the branch that
    moves toward the reference point (apex of the liquid cap).
    """
    deriv = _normalize_vector(derivative_fn(contact_t))
    if deriv is None:
        return None

    p_plus = np.asarray(point_fn(contact_t + step), dtype=np.float64)
    p_minus = np.asarray(point_fn(contact_t - step), dtype=np.float64)
    ref = np.asarray(reference_pt, dtype=np.float64)

    score_plus = inside_sign * _point_side_relative_to_baseline((float(p_plus[0]), float(p_plus[1])), baseline_coeffs)
    score_minus = inside_sign * _point_side_relative_to_baseline((float(p_minus[0]), float(p_minus[1])), baseline_coeffs)

    tol = 1e-10
    if score_plus > score_minus + tol:
        return deriv
    if score_minus > score_plus + tol:
        return -deriv

    # Tie-breaker: choose the neighbouring curve point that heads toward the liquid reference point.
    if np.linalg.norm(p_plus - ref) <= np.linalg.norm(p_minus - ref):
        return deriv
    return -deriv


def _compute_inside_contact_angle(
    contact_pt: Tuple[float, float],
    tangent_vec: Tuple[float, float],
    baseline_coeffs: Tuple[float, float, float],
    footprint_midpoint: Tuple[float, float]
) -> Optional[float]:
    """
    Compute inside-liquid contact angle as the angle between:
    - the substrate direction pointing into the wetted footprint
    - the interface tangent direction pointing along the liquid cap
    """
    baseline_in = _oriented_baseline_inside_direction(contact_pt, baseline_coeffs, footprint_midpoint)
    tangent_in = _normalize_vector(tangent_vec)

    if baseline_in is None or tangent_in is None:
        return None

    angle = _angle_deg_between(baseline_in, tangent_in)
    if angle is None:
        return None

    return float(max(0.0, min(180.0, angle)))


# ========================================================================
# FUNCTION TO COMPUTE CONTACT ANGLE FROM ELLIPSE
# ========================================================================

def compute_contact_angle_from_ellipse(
    ellipse_params: Dict,
    baseline_coeffs: Tuple[float, float, float]
) -> Optional[Dict]:
    """
    Compute INSIDE-LIQUID contact angle from rotated ellipse and baseline line.

    Important geometric fix:
    - The tangent orientation is selected using the neighbouring *ellipse points* on the
      correct cap branch, not by stepping along the tangent line.
    - This removes the common acute/obtuse flip error for internal contact angles.
    """
    a_line, b_line, c_line = baseline_coeffs
    x0 = ellipse_params['x0']
    y0 = ellipse_params['y0']
    a = ellipse_params['a']
    b = ellipse_params['b']
    theta = ellipse_params['theta']

    if a <= 1e-12 or b <= 1e-12:
        return None

    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    # Express baseline in ellipse-local coordinates (u, v)
    A = a_line * cos_t + b_line * sin_t
    B = -a_line * sin_t + b_line * cos_t
    C = a_line * x0 + b_line * y0 + c_line

    def uv_to_xy(u, v):
        x = x0 + u * cos_t - v * sin_t
        y = y0 + u * sin_t + v * cos_t
        return (float(x), float(y))

    def point_from_param(t):
        u = a * np.cos(t)
        v = b * np.sin(t)
        return uv_to_xy(u, v)

    def derivative_from_param(t):
        du = -a * np.sin(t)
        dv = b * np.cos(t)
        dx = du * cos_t - dv * sin_t
        dy = du * sin_t + dv * cos_t
        return (float(dx), float(dy))

    contact_data = []
    eps = 1e-9

    # Solve intersection between line and rotated ellipse in local coordinates.
    if abs(B) < eps:
        if abs(A) < eps:
            return None
        u_contact = -C / A
        v_sq = b**2 * (1 - (u_contact / a)**2)
        if v_sq < 0:
            if v_sq > -1e-10:
                v_sq = 0.0
            else:
                return None
        v = np.sqrt(v_sq)
        for vv in (v, -v):
            pt = uv_to_xy(u_contact, vv)
            t_contact = float(np.arctan2(vv / b, u_contact / a))
            contact_data.append({'point': pt, 'u': float(u_contact), 'v': float(vv), 't': t_contact})
    else:
        alpha_coeff = A**2 + (B * b / a)**2
        beta_coeff = 2 * A * C
        gamma_coeff = C**2 - (B * b)**2

        discriminant = beta_coeff**2 - 4 * alpha_coeff * gamma_coeff
        if discriminant < 0:
            if discriminant > -1e-10:
                discriminant = 0.0
            else:
                return None
        sqrt_disc = np.sqrt(discriminant)

        u1 = (-beta_coeff + sqrt_disc) / (2.0 * alpha_coeff)
        u2 = (-beta_coeff - sqrt_disc) / (2.0 * alpha_coeff)
        v1 = -(A * u1 + C) / B
        v2 = -(A * u2 + C) / B

        for u_contact, v_contact in ((u1, v1), (u2, v2)):
            pt = uv_to_xy(u_contact, v_contact)
            t_contact = float(np.arctan2(v_contact / b, u_contact / a))
            contact_data.append({'point': pt, 'u': float(u_contact), 'v': float(v_contact), 't': t_contact})

    if len(contact_data) < 2:
        return None

    contact_data.sort(key=lambda item: item['point'][0])
    left_data, right_data = contact_data[0], contact_data[1]
    left_pt, right_pt = left_data['point'], right_data['point']

    footprint_midpoint = (
        (left_pt[0] + right_pt[0]) / 2.0,
        (left_pt[1] + right_pt[1]) / 2.0
    )

    # Reference point on the liquid cap: highest point of the ellipse in world coordinates.
    t_ref = float(np.arctan2(b * cos_t, a * sin_t))
    reference_pt = point_from_param(t_ref)
    inside_sign = _sign_with_tolerance(_point_side_relative_to_baseline(reference_pt, baseline_coeffs))
    if inside_sign == 0:
        # Fallback: use the side of the ellipse centre if the reference point is numerically on the baseline.
        inside_sign = _sign_with_tolerance(_point_side_relative_to_baseline((x0, y0), baseline_coeffs))
        if inside_sign == 0:
            inside_sign = 1

    left_tan = _select_tangent_using_curve_branch(
        left_data['t'], point_from_param, derivative_from_param, baseline_coeffs, inside_sign, reference_pt
    )
    right_tan = _select_tangent_using_curve_branch(
        right_data['t'], point_from_param, derivative_from_param, baseline_coeffs, inside_sign, reference_pt
    )

    if left_tan is None or right_tan is None:
        return None

    left_angle = _compute_inside_contact_angle(left_pt, left_tan, baseline_coeffs, footprint_midpoint)
    right_angle = _compute_inside_contact_angle(right_pt, right_tan, baseline_coeffs, footprint_midpoint)

    if left_angle is None or right_angle is None:
        return None

    return {
        'left_angle': float(left_angle),
        'right_angle': float(right_angle),
        'left_point': left_pt,
        'right_point': right_pt,
        'left_tangent': (float(left_tan[0]), float(left_tan[1])),
        'right_tangent': (float(right_tan[0]), float(right_tan[1]))
    }


# ========================================================================
# FUNCTION TO COMPUTE CONTACT ANGLE FROM CIRCLE
# ========================================================================

def compute_contact_angle_from_circle(
    circle_params: Dict,
    baseline_coeffs: Tuple[float, float, float]
) -> Optional[Dict]:
    """
    Compute INSIDE-LIQUID contact angle from circle (simplified Young-Laplace).

    Uses the same curve-branch selection strategy as the ellipse version to avoid
    wrong tangent orientation near the contact line.
    """
    a_line, b_line, c_line = baseline_coeffs
    x0 = circle_params['x0']
    y0 = circle_params['y0']
    R = circle_params['R']

    if R <= 1e-12:
        return None
    if abs(a_line) < 1e-12 and abs(b_line) < 1e-12:
        return None

    def point_from_param(t):
        return (float(x0 + R * np.cos(t)), float(y0 + R * np.sin(t)))

    def derivative_from_param(t):
        return (float(-R * np.sin(t)), float(R * np.cos(t)))

    contact_data = []

    if abs(b_line) < 1e-9:
        if abs(a_line) < 1e-12:
            return None
        x = -c_line / a_line
        dy_sq = R**2 - (x - x0)**2
        if dy_sq < 0:
            if dy_sq > -1e-10:
                dy_sq = 0.0
            else:
                return None
        dy = np.sqrt(dy_sq)
        for y in (y0 + dy, y0 - dy):
            t_contact = float(np.arctan2((y - y0) / R, (x - x0) / R))
            contact_data.append({'point': (float(x), float(y)), 't': t_contact})
    else:
        k = a_line / b_line
        d = -c_line / b_line

        m = d - y0 - k * x0
        A_coeff = 1 + k**2
        B_coeff = -2 * k * m
        C_coeff = m**2 - R**2

        discriminant = B_coeff**2 - 4 * A_coeff * C_coeff
        if discriminant < 0:
            if discriminant > -1e-10:
                discriminant = 0.0
            else:
                return None

        sqrt_disc = np.sqrt(discriminant)
        u1 = (-B_coeff + sqrt_disc) / (2 * A_coeff)
        u2 = (-B_coeff - sqrt_disc) / (2 * A_coeff)

        for x in (u1 + x0, u2 + x0):
            y = -k * x + d
            t_contact = float(np.arctan2((y - y0) / R, (x - x0) / R))
            contact_data.append({'point': (float(x), float(y)), 't': t_contact})

    if len(contact_data) < 2:
        return None

    contact_data.sort(key=lambda item: item['point'][0])
    left_data, right_data = contact_data[0], contact_data[1]
    left_pt, right_pt = left_data['point'], right_data['point']

    footprint_midpoint = (
        (left_pt[0] + right_pt[0]) / 2.0,
        (left_pt[1] + right_pt[1]) / 2.0
    )

    reference_pt = (float(x0), float(y0 + R))
    inside_sign = _sign_with_tolerance(_point_side_relative_to_baseline(reference_pt, baseline_coeffs))
    if inside_sign == 0:
        inside_sign = _sign_with_tolerance(_point_side_relative_to_baseline((x0, y0), baseline_coeffs))
        if inside_sign == 0:
            inside_sign = 1

    left_tan = _select_tangent_using_curve_branch(
        left_data['t'], point_from_param, derivative_from_param, baseline_coeffs, inside_sign, reference_pt
    )
    right_tan = _select_tangent_using_curve_branch(
        right_data['t'], point_from_param, derivative_from_param, baseline_coeffs, inside_sign, reference_pt
    )

    if left_tan is None or right_tan is None:
        return None

    left_angle = _compute_inside_contact_angle(left_pt, left_tan, baseline_coeffs, footprint_midpoint)
    right_angle = _compute_inside_contact_angle(right_pt, right_tan, baseline_coeffs, footprint_midpoint)

    if left_angle is None or right_angle is None:
        return None

    return {
        'left_angle': float(left_angle),
        'right_angle': float(right_angle),
        'left_point': left_pt,
        'right_point': right_pt,
        'left_tangent': (float(left_tan[0]), float(left_tan[1])),
        'right_tangent': (float(right_tan[0]), float(right_tan[1]))
    }

# ========================================================================
# BASELINE-CONSTRAINED AUTOMATIC EDGE DETECTION
# ========================================================================

def _as_grayscale_uint8(image_array: np.ndarray) -> Optional[np.ndarray]:
    """Return a finite contiguous grayscale image suitable for OpenCV."""
    if not isinstance(image_array, np.ndarray) or image_array.size == 0:
        return None

    image = image_array
    if image.ndim == 3:
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            return None
    elif image.ndim != 2:
        return None

    if image.dtype == np.uint8:
        return np.ascontiguousarray(image)

    finite = np.nan_to_num(image, nan=0.0, posinf=255.0, neginf=0.0)
    max_value = float(np.max(finite))
    min_value = float(np.min(finite))
    if 0.0 <= min_value and max_value <= 1.0:
        finite = finite * 255.0
    return np.ascontiguousarray(np.clip(finite, 0, 255).astype(np.uint8))


def _baseline_clearance(
    points_px: np.ndarray,
    baseline_coeffs: Tuple[float, float, float],
    scale_x: float,
    scale_y: float,
    physical_height: float,
) -> np.ndarray:
    """Vertical physical distance from each image point to the baseline."""
    a_line, b_line, c_line = (float(value) for value in baseline_coeffs)
    if abs(b_line) <= 1e-12:
        raise ValueError("Baseline must not be vertical.")

    x_phys = points_px[:, 0].astype(np.float64) * scale_x
    y_phys = physical_height - (
        points_px[:, 1].astype(np.float64) * scale_y
    )
    baseline_y = -(a_line * x_phys + c_line) / b_line
    return y_phys - baseline_y


def _longest_valid_contour_arc(
    contour_points: np.ndarray,
    valid_mask: np.ndarray,
) -> Optional[np.ndarray]:
    """Return the strongest continuous contour run above the baseline."""
    point_count = len(contour_points)
    if point_count < 2 or not np.any(valid_mask):
        return None
    if np.all(valid_mask):
        return contour_points

    first_invalid = int(np.flatnonzero(~valid_mask)[0])
    start = (first_invalid + 1) % point_count
    rolled_points = np.concatenate(
        (contour_points[start:], contour_points[:start]), axis=0
    )
    rolled_valid = np.concatenate(
        (valid_mask[start:], valid_mask[:start]), axis=0
    )

    runs = []
    run_start = None
    for index, is_valid in enumerate(rolled_valid):
        if is_valid and run_start is None:
            run_start = index
        elif not is_valid and run_start is not None:
            runs.append(rolled_points[run_start:index])
            run_start = None
    if run_start is not None:
        runs.append(rolled_points[run_start:])
    if not runs:
        return None

    def run_score(run):
        if len(run) < 2:
            return 0.0
        segments = np.diff(run.astype(np.float64), axis=0)
        return float(np.sum(np.hypot(segments[:, 0], segments[:, 1])))

    return max(runs, key=run_score)


def _point_above_baseline_at_x(
    contact_x: float,
    baseline_coeffs: Tuple[float, float, float],
    scale_x: float,
    scale_y: float,
    physical_height: float,
    contact_offset_px: float,
) -> np.ndarray:
    """Build a pixel point at a controlled clearance above the baseline."""
    a_line, b_line, c_line = baseline_coeffs
    x_physical = contact_x * scale_x
    baseline_y_physical = -(
        a_line * x_physical + c_line
    ) / b_line
    baseline_y_pixel = (
        physical_height - baseline_y_physical
    ) / scale_y
    return np.array(
        [contact_x, baseline_y_pixel - contact_offset_px],
        dtype=np.float64,
    )


def _estimate_contact_point(
    side_points: np.ndarray,
    side_clearance_px: np.ndarray,
    baseline_coeffs: Tuple[float, float, float],
    scale_x: float,
    scale_y: float,
    physical_height: float,
    contact_offset_px: float,
    fit_limit_px: float,
    maximum_shift_px: float,
) -> np.ndarray:
    """Extrapolate a local droplet side to a point just above the baseline."""
    fit_mask = (
        (side_clearance_px >= contact_offset_px)
        & (side_clearance_px <= fit_limit_px)
    )
    fit_points = side_points[fit_mask]
    fit_clearance = side_clearance_px[fit_mask]
    boundary_x = float(side_points[0, 0])

    if len(fit_points) >= 4 and float(np.ptp(fit_clearance)) > 1.0:
        design = np.column_stack(
            (fit_clearance.astype(np.float64), np.ones(len(fit_clearance)))
        )
        slope, intercept = np.linalg.lstsq(
            design,
            fit_points[:, 0].astype(np.float64),
            rcond=None,
        )[0]
        contact_x = float(slope * contact_offset_px + intercept)
        contact_x = float(
            np.clip(
                contact_x,
                boundary_x - maximum_shift_px,
                boundary_x + maximum_shift_px,
            )
        )
    else:
        contact_x = boundary_x

    return _point_above_baseline_at_x(
        contact_x,
        baseline_coeffs,
        scale_x,
        scale_y,
        physical_height,
        contact_offset_px,
    )


def _trim_contour_to_liquid_cap(
    contour_arc: np.ndarray,
    baseline_coeffs: Tuple[float, float, float],
    scale_x: float,
    scale_y: float,
    physical_height: float,
    baseline_margin_pixels: float,
    contact_hint_points_px: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Remove low-clearance substrate tails and reconstruct both contact points.

    A connected substrate band can be part of the same binary component as the
    droplet. Its clearance from the baseline remains small, while the liquid cap
    grows rapidly towards the apex. The transition on each side defines the
    footprint; a local side fit then places the endpoint just above the baseline.
    """
    if contour_arc is None or len(contour_arc) < 7:
        return contour_arc

    points = contour_arc.astype(np.float64)
    if points[0, 0] > points[-1, 0]:
        points = points[::-1]

    clearance_physical = _baseline_clearance(
        points,
        baseline_coeffs,
        scale_x,
        scale_y,
        physical_height,
    )
    clearance_px = clearance_physical / scale_y
    apex_index = int(np.argmax(clearance_px))
    maximum_clearance_px = float(clearance_px[apex_index])
    if apex_index < 3 or apex_index > len(points) - 4:
        return points

    transition_px = max(
        baseline_margin_pixels + 1.0,
        min(10.0, maximum_clearance_px * 0.025),
    )
    left_low = np.flatnonzero(
        clearance_px[:apex_index] <= transition_px
    )
    right_low = np.flatnonzero(
        clearance_px[apex_index + 1:] <= transition_px
    )
    if len(left_low) == 0 or len(right_low) == 0:
        return points

    left_index = int(left_low[-1])
    right_index = int(apex_index + 1 + right_low[0])
    if right_index - left_index < 6:
        return points

    core = points[left_index:right_index + 1].copy()
    core_clearance_px = clearance_px[left_index:right_index + 1]
    core_apex_index = apex_index - left_index
    fit_limit_px = max(
        transition_px + 6.0,
        min(40.0, maximum_clearance_px * 0.12),
    )
    contact_offset_px = max(
        0.5,
        min(1.0, baseline_margin_pixels * 0.25),
    )
    maximum_shift_px = max(
        4.0,
        float(np.ptp(core[:, 0])) * 0.03,
    )

    left_contact = _estimate_contact_point(
        core[:core_apex_index + 1],
        core_clearance_px[:core_apex_index + 1],
        baseline_coeffs,
        scale_x,
        scale_y,
        physical_height,
        contact_offset_px,
        fit_limit_px,
        maximum_shift_px,
    )
    right_contact = _estimate_contact_point(
        core[core_apex_index:][::-1],
        core_clearance_px[core_apex_index:][::-1],
        baseline_coeffs,
        scale_x,
        scale_y,
        physical_height,
        contact_offset_px,
        fit_limit_px,
        maximum_shift_px,
    )
    if (
        contact_hint_points_px is not None
        and contact_hint_points_px.shape == (2, 2)
        and np.all(np.isfinite(contact_hint_points_px))
    ):
        hints = contact_hint_points_px[
            np.argsort(contact_hint_points_px[:, 0])
        ]
        hint_tolerance_px = max(
            6.0,
            float(np.ptp(core[:, 0])) * 0.12,
        )
        if abs(float(hints[0, 0]) - left_contact[0]) <= hint_tolerance_px:
            left_contact = _point_above_baseline_at_x(
                float(hints[0, 0]),
                baseline_coeffs,
                scale_x,
                scale_y,
                physical_height,
                contact_offset_px,
            )
        if abs(float(hints[1, 0]) - right_contact[0]) <= hint_tolerance_px:
            right_contact = _point_above_baseline_at_x(
                float(hints[1, 0]),
                baseline_coeffs,
                scale_x,
                scale_y,
                physical_height,
                contact_offset_px,
            )
    core[0] = left_contact
    core[-1] = right_contact
    return core


def _resample_contour_arc(
    contour_arc: np.ndarray,
    num_points: int,
) -> Optional[np.ndarray]:
    """Sample a contour at uniform arc-length intervals."""
    if contour_arc is None or len(contour_arc) < 2 or num_points <= 0:
        return None

    points = contour_arc.astype(np.float64)
    keep = np.ones(len(points), dtype=bool)
    keep[1:] = np.any(np.diff(points, axis=0) != 0, axis=1)
    points = points[keep]
    if len(points) < 2:
        return None

    segment_lengths = np.hypot(
        np.diff(points[:, 0]), np.diff(points[:, 1])
    )
    cumulative = np.concatenate(([0.0], np.cumsum(segment_lengths)))
    if cumulative[-1] <= 1e-12:
        return None

    targets = np.linspace(0.0, cumulative[-1], num_points)
    sampled = np.column_stack(
        (
            np.interp(targets, cumulative, points[:, 0]),
            np.interp(targets, cumulative, points[:, 1]),
        )
    )
    if sampled[0, 0] > sampled[-1, 0]:
        sampled = sampled[::-1]
    return sampled


def auto_detect_edge_points(
    image_array: np.ndarray,
    num_points: int,
    physical_width: float = 5.0,
    physical_height: float = 3.0,
    baseline_coeffs: Optional[Tuple[float, float, float]] = None,
    baseline_margin_pixels: float = 2.0,
    baseline_anchor_points: Optional[
        Sequence[Tuple[float, float]]
    ] = None,
) -> List[Tuple[float, float]]:
    """
    Detect the liquid-cap silhouette strictly above a user-defined baseline.

    The baseline first masks the substrate/reflection half-plane. Candidate
    contours must have meaningful height above that line. Low-clearance tails
    are removed, validated baseline anchors can pin the contact endpoints, and
    the resulting liquid-cap arc is sampled uniformly by arc length.
    """
    try:
        requested_points = int(num_points)
        width_phys = float(physical_width)
        height_phys = float(physical_height)
        margin_pixels = max(0.5, float(baseline_margin_pixels))
    except (TypeError, ValueError):
        return []
    if (
        requested_points <= 0
        or width_phys <= 0
        or height_phys <= 0
        or baseline_coeffs is None
        or len(baseline_coeffs) != 3
    ):
        return []

    image = _as_grayscale_uint8(image_array)
    if image is None:
        return []
    height_px, width_px = image.shape
    if height_px < 8 or width_px < 8:
        return []

    scale_x = width_phys / max(width_px - 1, 1)
    scale_y = height_phys / max(height_px - 1, 1)
    x_pixels = np.arange(width_px, dtype=np.float64)
    x_phys = x_pixels * scale_x
    a_line, b_line, c_line = (float(value) for value in baseline_coeffs)
    if (
        not np.all(np.isfinite((a_line, b_line, c_line)))
        or abs(b_line) <= 1e-12
    ):
        return []

    baseline_y = -(a_line * x_phys + c_line) / b_line
    y_phys = height_phys - (
        np.arange(height_px, dtype=np.float64)[:, None] * scale_y
    )
    above_baseline = y_phys >= baseline_y[None, :]
    if not np.any(above_baseline):
        return []

    contact_hint_points_px = None
    if baseline_anchor_points is not None:
        try:
            anchor_points = np.asarray(
                baseline_anchor_points,
                dtype=np.float64,
            )
            if (
                anchor_points.shape == (2, 2)
                and np.all(np.isfinite(anchor_points))
            ):
                contact_hint_points_px = np.column_stack(
                    (
                        anchor_points[:, 0] / scale_x,
                        (
                            height_phys - anchor_points[:, 1]
                        ) / scale_y,
                    )
                )
        except (TypeError, ValueError):
            contact_hint_points_px = None

    blurred = cv2.GaussianBlur(image, (7, 7), 0)
    masked_image = blurred.copy()
    masked_image[~above_baseline] = 255
    _, binary = cv2.threshold(
        masked_image,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )
    binary[~above_baseline] = 0

    kernel_size = int(round(min(height_px, width_px) * 0.006))
    kernel_size = min(9, max(3, kernel_size | 1))
    close_kernel = np.ones((kernel_size, kernel_size), np.uint8)
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_CLOSE, close_kernel
    )
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)
    )
    binary[~above_baseline] = 0
    binary[[0, -1], :] = 0
    binary[:, [0, -1]] = 0

    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if not contours:
        return []

    clearance_margin = margin_pixels * scale_y
    minimum_cap_height = max(6.0 * scale_y, 0.03 * height_phys)
    minimum_area = max(20.0, height_px * width_px * 0.00025)
    best_arc = None
    best_score = -np.inf

    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < minimum_area:
            continue
        contour_points = contour.reshape(-1, 2)
        if len(contour_points) < 6:
            continue
        try:
            clearance = _baseline_clearance(
                contour_points,
                (a_line, b_line, c_line),
                scale_x,
                scale_y,
                height_phys,
            )
        except ValueError:
            return []

        if float(np.max(clearance)) < minimum_cap_height:
            continue
        valid = clearance > clearance_margin
        arc = _longest_valid_contour_arc(contour_points, valid)
        if arc is None or len(arc) < 5:
            continue
        arc = _trim_contour_to_liquid_cap(
            arc,
            (a_line, b_line, c_line),
            scale_x,
            scale_y,
            height_phys,
            margin_pixels,
            contact_hint_points_px,
        )
        if arc is None or len(arc) < 5:
            continue

        x_span = float(np.ptp(arc[:, 0]))
        y_span = float(np.ptp(arc[:, 1]))
        if x_span < width_px * 0.02 or y_span < height_px * 0.02:
            continue
        arc_segments = np.diff(arc.astype(np.float64), axis=0)
        arc_length = float(
            np.sum(np.hypot(arc_segments[:, 0], arc_segments[:, 1]))
        )
        cap_height = float(np.max(clearance))
        score = arc_length * (1.0 + cap_height / height_phys)
        score += 0.01 * np.sqrt(area)
        if score > best_score:
            best_score = score
            best_arc = arc

    sampled = _resample_contour_arc(best_arc, requested_points)
    if sampled is None:
        return []

    x_values = sampled[:, 0] * scale_x
    y_values = height_phys - (sampled[:, 1] * scale_y)
    baseline_values = -(a_line * x_values + c_line) / b_line
    valid_output = y_values > baseline_values
    return [
        (float(x_value), float(y_value))
        for x_value, y_value, is_valid in zip(
            x_values, y_values, valid_output
        )
        if is_valid
    ]
