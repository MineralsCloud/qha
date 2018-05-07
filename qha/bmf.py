#!/usr/bin/env python3
"""
:mod: bmf
================================

.. module bmf
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Optional

import numpy as np


def bmf_energy(x, y, nv: int, xo, v, ntv, order: Optional[int] = 3):
    # Initializations of different sums involved in fitting.
    x1 = 0
    x2 = 0
    x3 = 0
    x4 = 0
    x5 = 0
    x6 = 0
    x7 = 0
    x8 = 0
    x9 = 0
    x10 = 0
    y1 = 0
    y2 = 0
    y3 = 0
    y4 = 0
    y5 = 0
    y6 = 0
    # Performing different sums
    for I in range(nv):
        x1 = x1 + x[I]
        x2 = x2 + x[I] ** 2
        x3 = x3 + x[I] ** 3
        x4 = x4 + x[I] ** 4
        x5 = x5 + x[I] ** 5
        x6 = x6 + x[I] ** 6
        x7 = x7 + x[I] ** 7
        x8 = x8 + x[I] ** 8
        x9 = x9 + x[I] ** 9
        x10 = x10 + (x[I] ** 5) * (x[I] ** 5)
        y1 = y1 + y[I]
        y2 = y2 + y[I] * x[I]
        y3 = y3 + y[I] * x[I] ** 2
        y4 = y4 + y[I] * x[I] ** 3
        y5 = y5 + y[I] * x[I] ** 4
        y6 = y6 + y[I] * x[I] ** 5

    r1 = nv * x2 - x1 ** 2
    r2 = nv * x3 - x1 * x2
    r3 = nv * x4 - x1 * x3
    r4 = nv * x5 - x1 * x4
    r5 = nv * x6 - x1 * x5
    r6 = nv * x4 - x2 ** 2
    r7 = nv * x5 - x2 * x3
    r8 = nv * x6 - x2 * x4
    r9 = nv * x7 - x2 * x5
    r10 = nv * x6 - x3 ** 2
    r11 = nv * x7 - x3 * x4
    r12 = nv * x8 - x3 * x5
    r13 = nv * x8 - x4 ** 2
    r14 = nv * x9 - x4 * x5
    r15 = nv * x10 - x5 ** 2

    s1 = nv * y2 - y1 * x1
    s2 = nv * y3 - y1 * x2
    s3 = nv * y4 - y1 * x3
    s4 = nv * y5 - y1 * x4
    s5 = nv * y6 - y1 * x5

    p1 = r1 * r6 - r2 ** 2
    p2 = r1 * r7 - r2 * r3
    p3 = r1 * r8 - r2 * r4
    p4 = r1 * r9 - r2 * r5
    p5 = r1 * r10 - r3 ** 2
    p6 = r1 * r11 - r3 * r4
    p7 = r1 * r12 - r3 * r5
    p8 = r1 * r13 - r4 ** 2
    p9 = r1 * r14 - r4 * r5
    p10 = r1 * r15 - r5 ** 2

    q1 = r1 * s2 - r2 * s1
    q2 = r1 * s3 - r3 * s1
    q3 = r1 * s4 - r4 * s1
    q4 = r1 * s5 - r5 * s1

    a1 = p1 * p5 - p2 ** 2
    a2 = p1 * p6 - p2 * p3
    a3 = p1 * p7 - p2 * p4
    a4 = p1 * p8 - p3 ** 2
    a5 = p1 * p9 - p3 * p4
    a6 = p1 * p10 - p4 ** 2

    b1 = p1 * q2 - p2 * q1
    b2 = p1 * q3 - p3 * q1
    b3 = p1 * q4 - p4 * q1

    u1 = a1 * a4 - a2 ** 2
    u2 = a1 * a5 - a2 * a3
    u3 = a1 * a6 - a3 ** 2

    v1 = a1 * b2 - a2 * b1
    v2 = a1 * b3 - a3 * b1

    if order == 5:
        Fn = (u1 * v2 - u2 * v1) / (u1 * u3 - u2 ** 2)
        E = (v1 - Fn * u2) / u1

    if order == 4:
        Fn = 0.0
        E = (v1 - Fn * u2) / u1

    if order == 3:
        Fn = 0.0
        E = 0.0

    D = (b1 - E * a2 - Fn * a3) / a1
    C = (q1 - D * p2 - E * p3 - Fn * p4) / p1
    B = (s1 - C * r2 - D * r3 - E * r4 - Fn * r5) / r1
    A = (y1 - B * x1 - C * x2 - D * x3 - E * x4 - Fn * x5) / nv

    """ Use fitting parameters to get energy """
    # Helmholtz free energy: F[T][V]
    fb = []
    for jn in range(ntv):
        fb.append(A + B * xo[jn] + C * xo[jn] ** 2.0 + D * xo[jn] ** 3.0 + E * xo[jn] ** 4.0 + Fn * xo[jn] ** 5.0)

    fb = np.array(fb)
    return fb


def bmf(fvib, V, xo_grid, v_grid, ntv, nt, order):
    """calculate the F(T,V),P(T,V), Bulk Modules:B(T,V)"""
    x = 0.5 * ((V[0] / V) ** (2 / 3) - 1)
    nv = len(V)
    f_v_t = np.empty((nt, ntv))  # initialize the F(T,V) array

    for i in range(nt):
        f_i = bmf_energy(x, fvib[i], nv, xo_grid, v_grid, ntv, order)
        f_v_t[i] = f_i
    return f_v_t
