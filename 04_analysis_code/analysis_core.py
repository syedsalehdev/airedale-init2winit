import io, contextlib
src = open("analysis.py").read().split("rows = []")[0]
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(src, g)
BYID = {i[0]: i for i in g["INV"]}
def steady_ids(ids, month, scale=1.0):
    return g["steady"]([BYID[i] for i in ids if month >= BYID[i][3]], scale)
