from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# timber classes (EC5 / EN 338) - f_m_k [N/mm2], E_0_mean [N/mm2]
TIMBER = {
    "C14": (14, 7000),
    "C16": (16, 8000),
    "C18": (18, 9000),
    "C20": (20, 9500),
    "C22": (22, 10000),
    "C24": (24, 11000),
    "C27": (27, 11500),
    "C30": (30, 12000),
}

# k_mod table (service class 1/2, simplified)
KMOD = {
    "permanent": 0.60,
    "medium": 0.80,
    "short": 0.90,
}

KDEF = {1: 0.60, 2: 0.80, 3: 2.00}


def calc(L, b, h, gk, qk, cls, sc, ld):
    # L in m, b/h in mm, gk/qk in kN/m
    fmk, E = TIMBER[cls]
    kmod = KMOD[ld]
    kdef = KDEF[sc]
    gammaM = 1.3
    gammaG = 1.35
    gammaQ = 1.5

    # design load
    qd = gammaG * gk + gammaQ * qk  # kN/m
    # ULS moment (simply supported, UDL)
    Md = qd * L * L / 8.0  # kNm
    Vd = qd * L / 2.0

    # section modulus
    W = b * h * h / 6.0  # mm3
    I = b * h * h * h / 12.0  # mm4

    # bending stress (convert kNm -> Nmm: *1e6)
    sigma_md = Md * 1e6 / W  # N/mm2
    fmd = kmod * fmk / gammaM
    uls_ratio = sigma_md / fmd

    # SLS deflection (characteristic combo, g+q)
    qk_sls = (gk + qk) * 1.0  # kN/m
    # w = 5*q*L^4 / (384*E*I), q in N/mm, L in mm, E in N/mm2, I in mm4
    q_nmm = qk_sls  # kN/m == N/mm
    Lmm = L * 1000.0
    w_inst = 5 * q_nmm * Lmm ** 4 / (384 * E * I)  # mm
    w_fin = w_inst * (1 + kdef)
    w_lim_inst = Lmm / 300.0
    w_lim_fin = Lmm / 250.0

    # diagrams
    N = 40
    xs = [i * L / N for i in range(N + 1)]
    Mx = [qd * x * (L - x) / 2.0 for x in xs]
    Vx = [qd * (L / 2.0 - x) for x in xs]
    # approx deflection shape: w(x) = q*x*(L^3 - 2Lx^2 + x^3) / (24 EI)  -> use SLS q
    wx_mm = []
    EI = E * I  # N*mm2
    q_sls_nmm = qk_sls
    for x in xs:
        xmm = x * 1000.0
        val = q_sls_nmm * xmm * (Lmm ** 3 - 2 * Lmm * xmm ** 2 + xmm ** 3) / (24 * EI)
        wx_mm.append(val)

    return {
        "inputs": dict(L=L, b=b, h=h, gk=gk, qk=qk, cls=cls, sc=sc, ld=ld),
        "qd": round(qd, 3),
        "Md": round(Md, 3),
        "Vd": round(Vd, 3),
        "fmd": round(fmd, 3),
        "sigma_md": round(sigma_md, 3),
        "uls_ratio": round(uls_ratio, 3),
        "uls_pass": uls_ratio <= 1.0,
        "w_inst": round(w_inst, 2),
        "w_fin": round(w_fin, 2),
        "w_lim_inst": round(w_lim_inst, 2),
        "w_lim_fin": round(w_lim_fin, 2),
        "sls_pass": (w_inst <= w_lim_inst) and (w_fin <= w_lim_fin),
        "chart": json.dumps({"xs": xs, "M": Mx, "V": Vx, "w": wx_mm}),
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.post("/", response_class=HTMLResponse)
def submit(
    request: Request,
    L: float = Form(5.0),
    b: float = Form(120),
    h: float = Form(240),
    gk: float = Form(2.0),
    qk: float = Form(3.0),
    cls: str = Form("C24"),
    sc: int = Form(1),
    ld: str = Form("medium"),
):
    r = calc(L, b, h, gk, qk, cls, sc, ld)
    return templates.TemplateResponse("index.html", {"request": request, "result": r})
