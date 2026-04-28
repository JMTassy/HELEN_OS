"""
Spectral certificate for finite Hermitian kernel matrices.

Implements the Tier I certificate from:
  "Computable Certificates for Finite-Band Averaged Weil Positivity
   via Reproducible Spectral Bounds" — Jean Marie Tassy Simeoni (2025)

Theorem 3.3 (Weyl's inequality):
  λ_min(T_hp) ≥ λ_min(T_ref) - AEON
  where AEON := ‖T_hp - T_ref‖_op

Non-sovereign. No side effects. No signing. Pure computation.
Signing and promotion are the caller's responsibility.
"""
from __future__ import annotations

import hashlib
import json
import datetime
from typing import Any

import numpy as np


class SpectralCertificate:
    """
    Deterministic finite-dimensional certificate.

    Inputs:
      T_ref     — declared high-precision reference matrix (np.ndarray, Hermitian)
      tolerance — declared drift tolerance for margin interpretation

    Usage:
      cert = SpectralCertificate(T_ref, tolerance=1e-6)
      result = cert.certify(T_hp)
    """

    def __init__(self, T_ref: np.ndarray, tolerance: float = 1e-6) -> None:
        if T_ref.ndim != 2 or T_ref.shape[0] != T_ref.shape[1]:
            raise ValueError("T_ref must be a square 2-D array")
        self.T_ref = np.asarray(T_ref, dtype=complex)
        self.tolerance = float(tolerance)
        self._lam_min_ref: float | None = None

    @property
    def lam_min_ref(self) -> float:
        if self._lam_min_ref is None:
            self._lam_min_ref = float(np.min(np.linalg.eigvalsh(self.T_ref)))
        return self._lam_min_ref

    def compute_aeon(self, T_hp: np.ndarray) -> float:
        """Operator-norm drift: ‖T_hp - T_ref‖_op (largest singular value)."""
        return float(np.linalg.norm(T_hp - self.T_ref, ord=2))

    def certify(self, T_hp: np.ndarray) -> dict[str, Any]:
        """
        Returns Tier I certificate dict.

        Fields:
          lambda_min_hp      — smallest eigenvalue of T_hp
          lambda_min_ref     — smallest eigenvalue of T_ref (cached)
          aeon               — operator-norm drift ‖T_hp - T_ref‖_op
          margin             — λ_min(T_ref) - AEON  (Weyl lower bound)
          is_positive_definite — margin > 0
          status             — "POSITIVE_DEFINITE" | "INCONCLUSIVE"
          diagnostics        — COMM, FDR, ALIAS (logged only, not in Tier I)
        """
        T_hp = np.asarray(T_hp, dtype=complex)
        if T_hp.shape != self.T_ref.shape:
            raise ValueError(
                f"T_hp shape {T_hp.shape} ≠ T_ref shape {self.T_ref.shape}"
            )

        eigvals_hp = np.linalg.eigvalsh(T_hp)
        lam_min_hp = float(np.min(eigvals_hp))
        aeon = self.compute_aeon(T_hp)
        margin = self.lam_min_ref - aeon

        status = "POSITIVE_DEFINITE" if margin > 0 else "INCONCLUSIVE"

        diagnostics = self._compute_diagnostics(T_hp, eigvals_hp)

        return {
            "lambda_min_hp": lam_min_hp,
            "lambda_min_ref": self.lam_min_ref,
            "aeon": aeon,
            "margin": margin,
            "is_positive_definite": margin > 0,
            "status": status,
            "tolerance": self.tolerance,
            "diagnostics": diagnostics,
        }

    def _compute_diagnostics(
        self, T_hp: np.ndarray, eigvals_hp: np.ndarray
    ) -> dict[str, float]:
        """
        Diagnostic channels (logged for falsification, never enter Tier I).
          COMM  — commutator stress ‖[D_c, T_hp]‖_op
          FDR   — flagged-mode drift ‖P_sig (T_hp - T_ref) P_sig‖_op
          ALIAS — not computable without the grid; returns 0.0 as sentinel
        """
        n = T_hp.shape[0]

        # D_c: discrete dilation (shift) operator
        D_c = np.zeros((n, n), dtype=complex)
        for j in range(n - 1):
            D_c[j, j + 1] = 1.0

        comm = np.linalg.norm(D_c @ T_hp - T_hp @ D_c, ord=2)

        # Flagged modes: |λ_i| ≤ tolerance
        sig_idx = np.where(np.abs(eigvals_hp) <= self.tolerance)[0]
        if sig_idx.size > 0:
            _, V = np.linalg.eigh(T_hp)
            V_sig = V[:, sig_idx]
            P_sig = V_sig @ V_sig.conj().T
            fdr = float(np.linalg.norm(P_sig @ (T_hp - self.T_ref) @ P_sig, ord=2))
        else:
            fdr = 0.0

        return {
            "COMM": float(comm),
            "FDR": fdr,
            "ALIAS": 0.0,  # requires grid — caller may inject
        }


def build_receipt(
    cert_output: dict[str, Any],
    object_id: str,
    params: dict[str, Any],
    prev_hash: str | None = None,
) -> dict[str, Any]:
    """
    Wrap cert output in a NON_SOVEREIGN receipt envelope.

    The returned receipt has validator_id=None and signature=None.
    It is INVALID for promotion until signed by an external validator.
    """
    receipt: dict[str, Any] = {
        "schema": "SPECTRAL_CERTIFICATE_RECEIPT_V1",
        "authority_status": "NON_SOVEREIGN",
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
                         .isoformat().replace("+00:00", "Z"),
        "object_id": object_id,
        "parameters": params,
        "lambda_min_hp": cert_output["lambda_min_hp"],
        "lambda_min_ref": cert_output["lambda_min_ref"],
        "aeon": cert_output["aeon"],
        "margin": cert_output["margin"],
        "status": cert_output["status"],
        "diagnostics": cert_output["diagnostics"],
        "prev_hash": prev_hash,
        "validator_id": None,
        "signature": None,
    }
    # Payload hash (content-addressed, before signing)
    payload_str = json.dumps(
        {k: v for k, v in receipt.items() if k not in ("validator_id", "signature")},
        sort_keys=True, default=str,
    )
    receipt["payload_hash"] = hashlib.sha256(payload_str.encode()).hexdigest()
    return receipt


def build_kernel_matrix(
    symbol_values: np.ndarray, grid: np.ndarray
) -> np.ndarray:
    """
    Construct T(J,c) from a pre-evaluated symbol and a 1-D grid.

    T_jk = 0.5 * (m_w(x_j - x_k) + m_w(x_k - x_j))

    symbol_values must be a function or pre-sampled array satisfying
    the symmetrisation. Here we accept a callable m_w(delta) -> float.
    """
    raise NotImplementedError(
        "Caller must provide symbol evaluation: "
        "supply T_ref and T_hp directly to SpectralCertificate."
    )
