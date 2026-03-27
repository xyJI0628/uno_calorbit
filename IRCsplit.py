import numpy

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def all_numbers(numlist):
    for s in numlist:
        if is_number(s) == False:
            return False
    return True

def id2elem(id):
    Element=['H' ,                                                                                                                                                      'He',
             'Li','Be',                                                                                                                        'B' ,'C' ,'N' ,'O' ,'F' ,'Ne',
             'Na','Mg',                                                                                                                        'Al','Si','P' ,'S' ,'Cl','Ar',
             'K' ,'Ca',                                                                      'Sc','Ti','V' ,'Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr',
             'Rb','Sr',                                                                      'Y' ,'Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I' ,'Xe',
             'Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W' ,'Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn',
             'Fr','Ra','Ac','Th','Pa','U' ,'Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og']
    return Element[id-1]

class Atom:
    def __init__(self, elem, xyz):
        self.elem = elem
        self.xyz = xyz
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]

def read_scan_output_IRC(scan):
    chg, mult, xyz, xyzs = 0, 0, [], []
    
    with open(scan, 'r') as read:
        flag = False
        for line in read.readlines():
            l = line.split()
            
            
            if len(l) >= 3 and l[0] == 'Charge' and l[1] == '=' and l[3] == 'Multiplicity' and l[4] == '=':
                chg = int(l[2])  
                mult = int(l[5])  
                continue

            
            if 'Input orientation:' in line:
                flag = True
                xyz = []
                continue
            if 'Distance matrix (angstroms)' in line:
                flag = False
                if xyz:
                    xyzs.append(xyz)
                continue
            if flag:
                if len(l) == 6 and all_numbers(l):
                    elem = int(l[1])
                    x = float(l[3])
                    y = float(l[4])
                    z = float(l[5])
                    xyz.append(Atom(elem, numpy.array([x, y, z])))
                    continue

    return chg, mult, xyzs

def generate_input_IRC(filename, chg, mult, xyz):
    with open(filename, 'w') as gen:
        gen.write(f'''\
%chk={filename[:-4]}.chk
%nprocs=28
#p upbe1pbe/def2svp  geom(checK) guess(checK) irc=(calcfc,maxpoint=30,stepsize=15,LQA)  
# em=gd3bj scrf=(solvent=dichloromethane) scf(maxcycle=512,xqc)

title

{chg} {mult}
''')
        for i in xyz:
            gen.write(f'{id2elem(i.elem):<4} {i.x:>16.8f} {i.y:>16.8f} {i.z:>16.8f}\n')
        gen.write('\n')

def main():
    scan_file = 'scan.log' 

    chg, mult, xyzs = read_scan_output_IRC(scan_file)

    if not xyzs:
        raise RuntimeError('No IRC geometries found in scan output.')

    mid = len(xyzs) // 2  

    i = 1
    for xyz in xyzs[:mid]:
        outname = f'irc_rev_{i}.gjf'
        generate_input_IRC(outname, chg, mult, xyz)
        i += 1  

    i = 1
    for xyz in xyzs[mid:]:
        outname = f'irc_fwd_{i}.gjf'
        generate_input_IRC(outname, chg, mult, xyz)
        i += 1  

    print(f'\nTotal IRC points processed: {len(xyzs)}')

if __name__ == '__main__':
    main()

