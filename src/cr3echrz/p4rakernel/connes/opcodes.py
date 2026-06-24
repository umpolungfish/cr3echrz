"""
opcodes.py — Connes Embedding automaton opcode library.

FSPLIT / FFUSE Frobenius invariant:
    norms = fsplit(factor)
    recon = ffuse(*norms)
    recon['spatial'].value   == 'spatial'    (always)
    recon['projective'].value == 'projective' (always)
This is mu o delta = id: C*-tensor norm bifurcation is losslessly reconstituted.
"""
from typing import Dict, Tuple
from cr3echrz.p4rakernel.connes import state as st
from cr3echrz.p4rakernel.connes.state import (II1Factor, Ultrapower, Norm, Embedding,
                   VOID, EMBEDDABLE, NON_EMBEDDABLE, PARADOX)


def vinit(name: str) -> II1Factor:
    """VINIT: genesis — create abstract II_1 factor, STATUS=VOID."""
    factor = II1Factor(name=name)
    st.state['factor']  = factor
    st.state['status']  = VOID
    st.state['history'] = [('VINIT', name)]
    return factor


def imscrib(factor: II1Factor) -> II1Factor:
    """IMSCRIB: establish hyperfinite self-similarity R =~ R otimes R."""
    if factor.name == 'R':
        factor.is_hyperfinite = True
        factor.trace = 'normalized_faithful_normal_trace'
    st.state['history'].append(('IMSCRIB', factor.is_hyperfinite))
    return factor


def tanch(factor: II1Factor) -> Ultrapower:
    """TANCH: construct R^omega as terminal anchor."""
    base = (factor if factor.is_hyperfinite
            else II1Factor(name='R', is_hyperfinite=True,
                           trace='normalized_faithful_normal_trace'))
    up = Ultrapower(base=base)
    st.state['ultrapower'] = up
    st.state['history'].append(('TANCH', base.name))
    return up


def fsplit(factor: II1Factor) -> Tuple[Norm, Norm]:
    """
    FSPLIT (delta): bifurcate C*-tensor norm into minimal (spatial) and
    maximal (projective) components.

    For hyperfinite factors the two norms coincide (is_equal=True) — this is
    the classical Connes theorem.  For non-hyperfinite factors, coincidence is
    exactly the Connes conjecture; pre-2020 is_equal is False (unknown).
    Post-2020, JNVWY proves norms diverge for L(F_2).
    """
    equal = factor.is_hyperfinite
    min_norm = Norm(value='spatial',    is_equal=equal)
    max_norm = Norm(value='projective', is_equal=equal)
    st.state['history'].append(('FSPLIT', (min_norm, max_norm)))
    return min_norm, max_norm


def ffuse(min_norm: Norm, max_norm: Norm) -> Dict[str, Norm]:
    """
    FFUSE (mu): reconstitute C*-tensor product from bifurcated norms.

    Frobenius roundtrip:
        ffuse(*fsplit(factor))['spatial'].value   == 'spatial'    (always)
        ffuse(*fsplit(factor))['projective'].value == 'projective' (always)
    Both hold for any factor: mu o delta = id.
    """
    result = {'spatial': min_norm, 'projective': max_norm}
    st.state['history'].append(('FFUSE', result))
    return result


def evalt(min_norm: Norm, max_norm: Norm) -> bool:
    """EVALT (T-arm): True iff min == max norm — factor embeds in R^omega."""
    result = min_norm.is_equal and max_norm.is_equal
    st.state['history'].append(('EVALT', result))
    return result


def evalf(min_norm: Norm, max_norm: Norm) -> bool:
    """EVALF (F-arm): True iff min != max norm — MIP*=RE obstruction present."""
    result = not (min_norm.is_equal and max_norm.is_equal)
    st.state['history'].append(('EVALF', result))
    return result


def afwd(factor: II1Factor, ultrapower: Ultrapower) -> Embedding:
    """AFWD: attempt trace-preserving *-homomorphism M -> R^omega."""
    success = factor.is_hyperfinite
    emb = Embedding(source=factor, target=ultrapower,
                    is_trace_preserving=True, success=success)
    st.state['history'].append(('AFWD', success))
    return emb


def arev(ultrapower: Ultrapower, factor: II1Factor) -> str:
    """AREV: reverse ultraproduct descent — derive complexity lower bound."""
    if factor.name == 'L(F_2)' and st.state['use_2020']:
        complexity = 'RE'   # Ji-Natarajan-Vidick-Wright-Yuen 2020
    else:
        complexity = 'unknown'
    st.state['history'].append(('AREV', complexity))
    return complexity


def clink() -> str:
    """CLINK: compose MIP* and RE — post-2020 formal equivalence MIP*=RE."""
    eq = 'MIP* == RE'
    st.state['history'].append(('CLINK', eq))
    return eq


def engagr(factor: II1Factor, pre2020: bool) -> int:
    """ENGAGR: engage Belnap STATUS for pre/post-2020 knowledge state."""
    if pre2020:
        new_status = EMBEDDABLE if factor.is_hyperfinite else PARADOX
    else:
        if factor.is_hyperfinite:
            new_status = EMBEDDABLE
        elif factor.name == 'L(F_2)':
            new_status = NON_EMBEDDABLE
        else:
            new_status = PARADOX
    st.state['status'] = new_status
    st.state['history'].append(('ENGAGR', new_status))
    return new_status


def ifix(factor: II1Factor, use_2020: bool) -> int:
    """IFIX: permanently fix STATUS — Ji-Natarajan-Vidick-Wright-Yuen 2020."""
    if use_2020:
        if factor.is_hyperfinite:
            fixed = EMBEDDABLE
        elif factor.name == 'L(F_2)':
            fixed = NON_EMBEDDABLE
        else:
            fixed = PARADOX
    else:
        fixed = st.state['status']   # retain ENGAGR value
    st.state['status'] = fixed
    st.state['history'].append(('IFIX', fixed))
    return fixed
