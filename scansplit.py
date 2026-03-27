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
        self.xyz  = xyz
        self.x    = xyz[0]
        self.y    = xyz[1]
        self.z    = xyz[2]

def read_scan_output(scan, program='g16'):
    if program == 'g16':
        return read_scan_output_g16(scan)
    elif program == 'orca':
        return read_scan_output_orca(scan)

def read_scan_output_g16(scan):
    chg, mult, xyz, xyzs = 0, 0, [], []
    with open(scan, 'r') as read:
        flag = False
        for line in read.readlines():
            l = line.split()
            if len(l) == 6 and l[0] == 'Charge' and l[3] == 'Multiplicity':
                chg = int(l[2])
                mult = int(l[5])
                continue
            if 'Standard orientation:' in line:
                flag = True
                xyz = []
                continue
            if 'Rotational constants' in line:
                flag = False
                continue
            if flag:
                if len(l) == 6 and all_numbers(l):
                    xyz.append(Atom(int(l[1]), numpy.array([float(l[3]), float(l[4]), float(l[5])])))
                    continue
            if 'Optimization completed.' in line:
                xyzs.append(xyz)
    return chg, mult, xyzs

def read_scan_output_orca(scan):
    ###
    return chg, mult, xyzs

def generate_input(filename, chg, mult, xyz, program='g16'):
    if program == 'g16':
        return generate_input_g16(filename, chg, mult, xyz)
    elif program == 'orca':
        return generate_input_orca(filename, chg, mult, xyz)

def generate_input_g16(filename, chg, mult, xyz):
    with open(filename, 'w') as gen:
        gen.write(f'''\
%nproc=40
%mem=160GB
%chk={filename[:-4]}.chk
#p uhf/def2tzvp nosymm int=nobasistransform 5d 7f
stable=opt scf(maxcyc=512,xqc)

title

{chg} {mult}
''')
        for i in xyz:
            gen.write(f'{id2elem(i.elem):<4} {i.x:>16.8f} {i.y:>16.8f} {i.z:>16.8f}\n')
        gen.write('\n')

def generate_input_orca(filename, chg, mult, xyz):
    ###
    return

# python scansplit.py -i g16 -o g16 -s scan.log
def printUsage():
    print('''python scansplit.py -i g16 -o g16 -s scan.log''')

def main():
    scan = None
    input_program = 'g16'
    output_program = 'g16'

    import sys, getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:o:s:')
    except getopt.GetoptError:
        printUsage()
        sys.exit(-1)
    for opt, arg in opts:
        if opt == '-h':
            printUsage()
        elif opt == '-i':
            input_program = arg
        elif opt == '-o':
            output_program = arg
        elif opt == '-s':
            scan = arg

    chg, mult, xyzs = read_scan_output(scan, program=input_program)
    for i in range(len(xyzs)):
        generate_input(f'{scan[:-4]}-{1+i}.gjf', chg, mult, xyzs[i], program=output_program)

if __name__ == '__main__':
    main()