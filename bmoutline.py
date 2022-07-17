import gpath

bitmap =  [
    [0,1,1,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,1,0,1,0,1,0],
    [1,1,0,0,1,1,0,0,1,0,0],
    [1,1,0,0,1,1,0,1,0,1,0],
    [1,1,1,1,1,1,0,0,0,0,0],
    [0,1,1,1,1,0,0,1,1,0,1],
    [0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,1,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
]

def edges(bm):
    w = len(bm[0])
    h = len(bm)

    he = [ [b-a for a,b in zip(A,B)] for A,B in zip([[0]*w]+bm, bm+[[0]*w]) ]
    ve = [ [a-b for a,b in zip([0]+A,A+[0])] for A in bm ]

    for i, r in enumerate(he):
        print('+' + '+'.join('← →'[e+1]*2 for e in r) + '+')
        if i < len(ve):
            print('  '.join('↑ ↓'[e+1] for e in ve[i]))

    def find_he():
        for i, A in enumerate(he):
            for j, e in enumerate(A):
                if he[i][j] == 1:
                    return (i,j)

    def follow_cycle(i0, j0):
        #starting with the horizontal right facing edge at (i,j)
        assert he[i0][j0] == 1
        d0 = 0
        j0 = j0+1
        i = i0
        j = j0
        d = d0
        while True:
            for dn in [-1, 0, 1]:
                dn = (dn+d)%4
                if dn == 0 and j<w and he[i][j] == 1:
                    he[i][j] = 0
                    if dn != d:
                        yield(i,j)
                    j += 1
                    d = dn
                    break
                elif dn == 1 and i<h and ve[i][j] == 1:
                    ve[i][j] = 0
                    if dn != d:
                        yield(i,j)
                    i += 1
                    d = dn
                    break
                elif dn == 2 and j>0 and he[i][j-1] == -1:
                    he[i][j-1] = 0
                    if dn != d:
                        yield(i,j)
                    j -= 1
                    d = dn
                    break
                elif dn == 3 and i>0 and ve[i-1][j] == -1:
                    ve[i-1][j] = 0
                    if dn != d:
                        yield(i,j)
                    i -= 1
                    d = dn
                    break
            else:
                assert False, (i,j,d)

            if (i,j,d) == (i0, j0, d0):
                break

    path = gpath.Path()
    e = find_he()
    while e is not None:
        points = iter(follow_cycle(*e))
        i,j = next(points)
        path.moveto(j,i)
        for i,j in points:
            path.lineto(j,i)
        e = find_he()
    return path

if __name__ == '__main__':
    path = edges(bitmap)
    print(path.svg())
    print(path.cff())
