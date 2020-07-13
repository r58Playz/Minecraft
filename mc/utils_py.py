import sys
 
def normalize(pos): 
    x,y,z = pos
    return round(x),round(y),round(z)
def flatten(lst): 
    return sum(map(list,lst),[])
def cube_vertices(pos,n=0.5):
    x,y,z = pos
    v = tuple((x+X,y+Y,z+Z) for X in (-n,n) for Y in (-n,n) for Z in (-n,n))
    return tuple(tuple(k for j in i for k in v[j]) for i in ((0,1,3,2),(5,4,6,7),(0,4,5,1),(3,7,6,2),(4,0,2,6),(1,5,7,3)))
def delete_last_line():
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')
