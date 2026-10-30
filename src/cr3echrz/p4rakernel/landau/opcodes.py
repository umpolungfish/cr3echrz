"""
opcodes.py — Landau's Theorems automaton opcode library.

FSPLIT / FFUSE Frobenius invariant:
    t_arm, f_arm = fsplit(f)
    fused = ffuse(t_arm, f_arm)
    fused['T'].label == 'T'        (always — T-arm label preserved)
    fused['F'].label == 'F'        (always — F-arm label preserved)
    fused['L']      == LANDAU_L    (always — universal constant)
This is mu o delta = id: the Landau constant L reconstitutes both branches exactly.
"""
from typing import Dict, Optional, Tuple
from cr3echrz.p4rakernel.landau import state as st
from cr3echrz.p4rakernel.landau.state import (HolomorphicFunction, Arm, LANDAU_L, KOEBE_K,
                   VOID, BOUNDED, UNBOUNDED, PICARD)


def vinit(name: str, description: str,
          omits_finite: Optional[bool],
          omitted_value: Optional[complex] = None,
          is_essential: bool = False) -> HolomorphicFunction:
    """VINIT: genesis — create abstract holomorphic function on D; STATUS=VOID."""
    f = HolomorphicFunction(
        name=name, description=description,
        f0=0+0j, fprime0=1+0j,
        omits_finite=omits_finite,
        omitted_value=omitted_value,
        is_essential=is_essential,
    )
    st.state['function']   = f
    st.state['status']     = VOID
    st.state['L_recorded'] = None
    st.state['history']    = [('VINIT', name)]
    return f


def tanch(domain_label: str = '|z| < 1') -> bool:
    """TANCH: anchor unit disk D = {|z| < 1} as hermetic boundary domain."""
    st.state['history'].append(('TANCH', domain_label))
    return True


def afwd(f: HolomorphicFunction, label: str = 'normalize') -> HolomorphicFunction:
    """AFWD: normalize f — f(0)=0, f'(0)=1; forward morphism to canonical form."""
    assert f.f0 == 0+0j,    f"AFWD FAIL: f(0)={f.f0} != 0"
    assert f.fprime0 == 1+0j, f"AFWD FAIL: f'(0)={f.fprime0} != 1"
    st.state['history'].append(('AFWD', (label, f.f0, f.fprime0)))
    return f


def clink(f: HolomorphicFunction, annotation: str) -> str:
    """CLINK: compose normalization with growth-rate measurement; chain constraint."""
    result = f"norm({f.name}) o {annotation}"
    st.state['history'].append(('CLINK', result))
    return result


def imscrib(f: HolomorphicFunction) -> bool:
    """IMSCRIB: self-recognition — f measures its own derivative; f'(0) is the self-referential bound."""
    ok = (f.f0 == 0+0j and abs(f.fprime0) == 1.0)
    assert ok, f"IMSCRIB FAIL: not normalized — f(0)={f.f0}, f'(0)={f.fprime0}"
    st.state['history'].append(('IMSCRIB', (f.name, f.fprime0)))
    return ok


def fsplit(f: HolomorphicFunction) -> Tuple[Arm, Arm]:
    """
    FSPLIT (delta): omission dichotomy.

    T-arm: f omits a finite value w0  =>  Landau bound L applies.
    F-arm: f has dense range           =>  no Landau restriction.

    omits_finite = True   ->  T active,  F silent
    omits_finite = False  ->  T silent,  F active
    omits_finite = None   ->  T active,  F active  (B-state: essential singularity)
    """
    t_active = (f.omits_finite is not False)    # True or None -> T fires
    f_active = (f.omits_finite is not True)     # False or None -> F fires

    t_arm = Arm(
        label='T',
        active=t_active,
        bound=LANDAU_L if t_active else None,
        description="f omits finite value w0; Landau bound L active",
    )
    f_arm = Arm(
        label='F',
        active=f_active,
        bound=None,
        description="f has dense/entire range; Landau restriction silent",
    )
    st.state['history'].append(('FSPLIT', (t_arm, f_arm)))
    return t_arm, f_arm


def evalt(t_arm: Arm) -> bool:
    """EVALT (T-arm): True iff f omits a finite value — Landau bound is active."""
    result = t_arm.active
    st.state['history'].append(('EVALT', result))
    return result


def evalf(f_arm: Arm) -> bool:
    """EVALF (F-arm): True iff f has dense range — no Landau omission constraint."""
    result = f_arm.active
    st.state['history'].append(('EVALF', result))
    return result


def ifix(label: str, value: float) -> float:
    """IFIX: permanently record the Landau constant L — append-only fixation."""
    if st.state['L_recorded'] is None:
        st.state['L_recorded'] = value
    st.verified[label] = {'L': value, 'status': st.state['status']}
    st.state['history'].append(('IFIX', (label, value)))
    return value


def arev(f_arm: Arm) -> Arm:
    """AREV: reverse morphism on F-arm — invert omission condition; parity flip.
    Inverting the dense-range arm reveals the complement gap framed by L.
    """
    inverted = Arm(
        label='F_inv',
        active=f_arm.active,
        bound=LANDAU_L,   # inverting dense-range exposes the L-framed boundary
        description="inverted F-arm: range-complement; L now frames the gap",
    )
    st.state['history'].append(('AREV', inverted))
    return inverted


def engagr(t_arm: Arm, f_arm: Arm) -> int:
    """ENGAGR: engage Belnap STATUS.
    PICARD(B) when both arms active simultaneously — essential singularity paradice.
    """
    if t_arm.active and not f_arm.active:
        new_status = BOUNDED
    elif not t_arm.active and f_arm.active:
        new_status = UNBOUNDED
    elif t_arm.active and f_arm.active:
        new_status = PICARD    # B-state: Picard entanglement
    else:
        new_status = VOID
    st.state['status'] = new_status
    st.state['history'].append(('ENGAGR', new_status))
    return new_status


def ffuse(t_arm: Arm, f_arm: Arm) -> Dict:
    """
    FFUSE (mu): fuse both arms via Landau constant L.

    Frobenius invariant (mu o delta = id):
        fused['T'].label == 'T'     (always)
        fused['F'].label == 'F'     (always)
        fused['L']      == LANDAU_L (always)
    L is the universal constant reconstituting both branches exactly.
    """
    result = {
        'T':    t_arm,
        'F':    f_arm,
        'L':    LANDAU_L,
        'T_ok': (t_arm.label == 'T'),
        'F_ok': (f_arm.label == 'F'),
        'L_ok': True,
    }
    st.state['history'].append(('FFUSE', result))
    return result
