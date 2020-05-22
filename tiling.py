import math

""" Calculates an optimal regular tiling for a BitWrk render of specified resolution.
    A regular tiling of a surface of dimensions WxH is specified by numbers u,v > 0
    denoting the number of tiles along the X and Y axis, respectively. An optimal
    tiling minimizes the sum of edge lengths, H*(u+1) + W*(v+1), and thereby also
    minimizes Hu+Wv.
    A tiling is feasible if the largest tile has area w*h <= C, with
    w = ceil(W/u) and h = ceil(H/v)
"""
"""
    지정된 분해능의 BitWrk 렌더에 대한 최적의 정규 타일링 계산.

    치수 WxH 표면의 정규 타일링은 각각 X축과 Y축을 따라 타일 수를 나타내는 숫자 u,v > 0으로 지정된다.
    최적 타일링은 에지 길이의 합, H*(u+1) + W*(v+1)를 최소화하여 Hu+Wv도 최소화한다.

    가장 큰 타일의 면적이 w*h <= C이고 w = ceil(W/u) 및 h = ceil(H/v)이면 타일링이 가능하다.
"""

def optimal_tiling(W, H, C):
    # Starting with an edge length <= sqrt(C) guarantees a feasible initial value.
    L = math.floor(math.sqrt(C))
    # ceil(W/u) and ceil(H/v) must both be <= L
    uv = (int(math.ceil(W / L)), int(math.ceil(H / L)))

    def is_feasible(uv):
        u, v = uv
        return u > 0 and v > 0 and math.ceil(W / u) * math.ceil(H / v) <= C

    if H > W:
        def walk(uv):
            u, v = uv
            yield (u - 1, v)
            yield (u, v - 1)
    else:
        def walk(uv):
            u, v = uv
            yield (u, v - 1)
            yield (u - 1, v)

    if not is_feasible(uv):
        raise RuntimeError(uv)

    found = True
    while found:
        # print("Evaluating", uv)
        found = False
        for candidate in walk(uv):
            if is_feasible(candidate):
                found = True
                uv = candidate
                break
    return uv
