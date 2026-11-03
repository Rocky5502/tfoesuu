import math
import numpy as np
from p19_sequential_audit import P,S,TAU,quartet,one_round_increments,matched_group,boundary_group,DELTA

def test_null_matched_patch_deltas_identical_on_all_tapes():
    tapes=np.linspace(0,1,200001)
    a,b,c,e=quartet(tapes,0.12,False,'matched')
    assert np.array_equal(b.astype(int)-a.astype(int),e.astype(int)-c.astype(int))

def test_alternative_matched_witness_fraction_exact_tape_grid():
    tapes=(np.arange(100000)+.5)/100000
    a,b,c,e=quartet(tapes,0.07,True,'matched')
    w=(b.astype(int)-a.astype(int))-(e.astype(int)-c.astype(int))
    assert np.count_nonzero(w)==7000
    assert set(np.unique(w))=={0,1}

def test_boundary_three_mass_law_and_lr():
    d=.05;r=1-P-S-TAU
    assert math.isclose(P+S+TAU+r,1)
    tapes=(np.arange(100000)+.5)/100000
    for alt, a_expected,b_expected in ((False,TAU,r),(True,TAU+d,r-d)):
        ll=one_round_increments(tapes,d,alt)
        ap=math.log((TAU+d)/TAU);bp=math.log((r-d)/r)
        assert abs(np.mean(np.isclose(ll,ap))-a_expected)<1e-9
        assert abs(np.mean(np.isclose(ll,bp))-b_expected)<1e-9
        kl=TAU*math.log(TAU/(TAU+d))+r*math.log(r/(r-d))
        if not alt: assert abs(-float(ll.mean())-kl)<1e-9

def test_witness_exact_miss_probability():
    d=.07; L=math.ceil(math.log(DELTA)/math.log1p(-d))
    assert (1-d)**L<=DELTA
    assert (1-d)**(L-1)>DELTA

def test_small_seeded_smoke_no_cap_and_correct_null():
    rounds,rejected,L=matched_group(np.random.default_rng(31),.07,False,200)
    assert not rejected.any() and np.all(rounds==L)
    rounds,rejected,hits=boundary_group(np.random.default_rng(32),.07,False,200)
    assert hits==0 and np.all(rounds>0)

def test_exact_kl_quadratic_and_linear_limits():
    r=1-P-S-TAU
    for d in [1e-3,1e-4,1e-5]:
        k=TAU*math.log(TAU/(TAU+d))+r*math.log(r/(r-d))
        ratio=k/(.5*d*d*(1/TAU+1/r))
        assert abs(ratio-1)<.02
        ctrl=r*math.log(r/(r-d))
        assert abs(ctrl/d-1)<.02
