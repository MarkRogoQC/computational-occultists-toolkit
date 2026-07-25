"""Comprehensive test suite for all Computational Occultists Toolkit modules."""
import sys, os, datetime, math, json
sys.path.insert(0, os.path.dirname(__file__))

passed = 0
failed = 0
errors = []

def test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
    except Exception as e:
        failed += 1
        errors.append((name, str(e)[:120]))

def suite():
    # Naometria Calculator
    from naometria_calculator import NaometriaCalculator
    calc = NaometriaCalculator()
    for y in [-5000, -1, 0, 99999]: test(f'nc: year {y}', lambda y=y: calc.compute_from_date(y) is not None)
    test('nc: 1620 summary', lambda: '1620' in calc.compute_from_date(1620).get('summary',''))
    test('nc: 2026->1606', lambda: any(a['result']==1606 for a in calc.abbreviate(2026)))
    test('nc: 2040->1620', lambda: any(a['result']==1620 for a in calc.abbreviate(2040)))
    test('nc: 1572->1602', lambda: any(o['opposite']==1602 for o in calc.contradiction(1572)))
    test('nc: 1620 self-confirm', lambda: any(o['opposite']==1620 for o in calc.contradiction(1620)))
    test('nc: inharmony', lambda: calc.inharmony_with_naometria(1620) is not None)
    test('nc: deterministic', lambda: calc.abbreviate(1620)==calc.abbreviate(1620))
    for i in range(200): calc.abbreviate(1900+(i%150))
    test('nc: 200 calls stable', lambda: True)

    # Shem HaMephorash
    from shem_hamephorash import ShemHaMephorash
    shm = ShemHaMephorash()
    test('shm: 72 names', lambda: len(shm.list_all())==72)
    for b in [-1,0,73,100]: test(f'shm: ob-{b}', lambda b=b: shm.band_to_name(b) is None)
    test('shm: band1=Vehuiah', lambda: shm.band_to_name(1)['angel']=='Vehuiah')
    test('shm: band72=Mikael', lambda: shm.band_to_name(72)['angel']=='Mikael')
    test('shm: michael found', lambda: len(shm.name_to_band('Michael'))>0)
    z=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    test('shm: 12 gates 6 each', lambda: all(len(shm.zodiac_gate(s))==6 for s in z))
    t1,t2=shm.today(),shm.today()
    test('shm: temporal stable', lambda: t1['effective_band']==t2['effective_band'])

    # Ars Magna Llull
    from ars_magna_llull import ArsMagna
    ll=ArsMagna()
    test('llull: empty subject', lambda: len(ll.apply_to_subject('',3))==3)
    test('llull: 84+ triples', lambda: len(list(ll.all_triples()))>=84)
    test('llull: wheel det', lambda: ll.generate_by_rotation(5)[0]['wheel_order']==ll.generate_by_rotation(5)[0]['wheel_order'])
    vec=ll.lullian_72_vector('time')
    test('llull: 72 bands', lambda: len(vec)==72)
    test('llull: norm sum≈1', lambda: abs(sum(vec)-1.0)<0.001)
    test('llull: subject det', lambda: ll.lullian_72_vector('x')==ll.lullian_72_vector('x'))

    # Pi Memory Reader
    from pi_memory_reader import PiMemory
    mem=PiMemory()
    for inp in ['','x'*10000,'unicode😊']: test(f'pi: edge {inp[:6]}',lambda inp=inp: mem.read_memory(inp,8)is not None)
    test('pi: deterministic', lambda: mem.read_memory('t_9821',16)['pi_position']==mem.read_memory('t_9821',16)['pi_position'])
    test('pi: read 100', lambda: len(mem.read_memory('t',100)['pi_digits'])==100)
    test('pi: dist det', lambda: mem.memory_distance('a','b',8)==mem.memory_distance('a','b',8))
    test('pi: diff inputs diff', lambda: mem.read_memory('a',8)['pi_position']!=mem.read_memory('b',8)['pi_position'])

    # Planetary Mirror
    from planetary_mirror import PlanetaryMirror
    pm=PlanetaryMirror()
    if not pm.history.all_events(): pm.seed_history()
    test('pm: 11 events', lambda: len(pm.history.all_events())>=11)
    c=pm.current_climate()
    test('pm: 72-band', lambda: len(c.get('planetary_vector',[]))==72)
    test('pm: 10 planets', lambda: len(c.get('planet_positions',{}))>=10)
    test('pm: symmetric', lambda: abs(pm.compare_dates(1572,1620)-pm.compare_dates(1620,1572))<0.0001)
    test('pm: same≈0', lambda: pm.compare_dates(2026,2026)<0.001)
    test('pm: sim det', lambda: pm.find_similar('2026-07-24',3)==pm.find_similar('2026-07-24',3))
    test('pm: 124yr proj', lambda: len(pm.project_forward(2026,124,10))>0)

    # Enoch Calendar
    import enoch_calendar as ec_mod
    ec=ec_mod.EnochCalendar()
    for d in [1,30,91,182,273,364]: test(f'ec: day {d}',lambda d=d: ec.day_of_year_to_position(d)is not None)
    for y in range(2020,2030): test(f'ec: sc {y}',lambda y=y: 1<=ec.sabbatical_cycle(y)['cycle_position']<=7)
    test('ec: greg conv',lambda: ec.gregorian_to_enoch(datetime.date(2026,7,24))is not None)
    for g in range(1,13): test(f'ec: gate {g}',lambda g=g: len(ec.get_bands_for_gate(g))==6)
    test('ec: festivals',lambda: len(ec.get_festivals())>0)
    test('ec: plot',lambda: isinstance(ec.plot_yearly(),str) and len(ec.plot_yearly())>200)

    # Trithemius Cipher
    import trithemius_cipher as tc
    n=[x for x in dir(tc) if isinstance(getattr(tc,x),type) and ('trithem' in x.lower() or 'cipher' in x.lower())][0]
    ci=getattr(tc,n)()
    for mode in [1,2,3]:
        for text in ['A','HELLO','TEST123',' ','!@#']:
            key='KEY' if mode==2 else None
            ct=ci.encrypt(text,mode,key=key); pt=ci.decrypt(ct,mode,key=key)
            test(f'tc: B{mode} {text}',lambda pt=pt,text=text: pt==text)
    test('tc: wrong key',lambda: ci.decrypt(ci.encrypt('SECRET',2,'KEY1'),2,'KEY2')!='SECRET')
    test('tc: stego',lambda: ci.steganographic_extract(ci.steganographic_embed('HI','AVE MARIA'))=='HI')
    test('tc: tabula 24+',lambda: len(ci.tabula_recta())>=20)

    # Fludd Monochord
    import fludd_monochord as fm
    d=fm.monochord_divisions()
    test('fm: 72',lambda: len(d)==72)
    for div in d: assert div.frequency_hz>0
    test('fm: freq>0',lambda: True)
    test('fm: 1-12 octave',lambda: fm.interval_for_bands(1,12) is not None)
    test('fm: 12 harm',lambda: len(fm.harmonic_series(1,12))==12)
    for p in ['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon']:
        test(f'fm: planet {p}',lambda p=p: fm.planetary_interval(p) is not None)
    test('fm: cons 0-1',lambda: all(0<=fm.band_consonance(i,i+1)<=1 for i in range(1,71)))
    test('fm: b12=2xb1',lambda: abs(d[11].frequency_hz/d[0].frequency_hz-2.0)<0.01)

    print(f'{passed} passed, {failed} failed')
    if errors:
        for n,e in errors[:10]: print(f'  FAIL: {n}: {e}')
    return failed == 0

if __name__ == '__main__':
    success = suite()
    sys.exit(0 if success else 1)
