"""Ranking das Freguesias G12: os 66 confrontos entre os 12 grandes, últimos 30 jogos oficiais.

Uso:  python3 scripts/calcular_g12.py
Entrada: dados/classicos_g12.json, dados/jogos.csv (14 clássicos locais) e dados/jogos_g12.csv (52 interestaduais)
Saída:  data/g12_*.json (aba G12, 52 interestaduais, g12.html) e data/g12c_*.json (aba G12 com clássicos, 66, g12-classicos.html), mais csv/

Mesmo método do ranking local (dados/pesos.json): recência por bloco de 10 jogos, peso de importância,
jogo extra para quem avançou em cada mata-mata. Diferenças: janela de 30 jogos (recortes 30/20/10),
"forma" dos últimos 5 (fora do ranking), índice por mando (jogos em campo neutro ficam fora) e ranking por clube.
"""
import csv, json, os, datetime as dt
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *x: os.path.join(RAIZ, *x)
PESOS = json.load(open(P("dados", "pesos.json"), encoding="utf-8"))
CLASSICOS = json.load(open(P("dados", "classicos_g12.json"), encoding="utf-8"))
REC = PESOS["recencia"]
W = PESOS["importancia"]
N = 30
JANELAS = [30, 20, 10]
FILTROS = ["Todas", "Brasileirão", "Copas", "Mata-mata"]
KO_BASE = {"SF", "F", "QF", "1/8", "1/16", "4F", "FP"}
COMPNOME = {"BR": "Brasileirão", "SB": "Série B", "CB": "Copa do Brasil", "LIB": "Libertadores", "SUL": "Sul-Americana",
            "REC": "Recopa", "SUP": "Supercopa", "PL": "Primeira Liga", "NE": "Copa do Nordeste", "MUN": "Mundial de Clubes"}
ESTNOME = {"RJ": "Carioca", "SP": "Paulistão", "RS": "Gauchão", "MG": "Mineiro"}
FASENOME = {"F": "Final", "SF": "Semifinal", "QF": "Quartas", "1/8": "Oitavas", "1/16": "16 avos", "4F": "4ª fase",
            "3F": "3ª fase", "2F": "2ª fase", "1F": "1ª fase", "5F": "5ª fase", "PO": "Playoff"}


def ko(g):
    f = g["fase"]
    if g["comp"] in ("CB", "LIB", "SUL", "SUP", "REC", "MUN"):
        # copas: tudo é eliminatório, menos rodada (R..) e grupo (no oGol, número do grupo na Libertadores e na Sul-Americana)
        if f.startswith("R") or f in ("", "-") or (g["comp"] in ("LIB", "SUL") and f.isdigit()):
            return False
        return True
    return f in KO_BASE


def ler():
    por = defaultdict(list)
    ids = {c["id"] for c in CLASSICOS}
    for arq in ("jogos.csv", "jogos_g12.csv"):
        caminho = P("dados", arq)
        if not os.path.exists(caminho):
            continue
        for r in csv.DictReader(open(caminho, encoding="utf-8")):
            if r["classico"] not in ids:
                continue
            pen = (int(r["pen_mandante"]), int(r["pen_visitante"])) if r["pen_mandante"] else None
            por[r["classico"]].append(dict(data=r["data"], m=r["mandante"], v=r["visitante"], gm=int(r["gm"]), gv=int(r["gv"]),
                                          comp=r["competicao"], temp=r["temporada"], fase=r["fase"], pen=pen, tipo=r["tipo"],
                                          vantagem=r["avancou_por_vantagem"], neutro=r.get("neutro", "") == "S", obs=r.get("obs", "")))
    for k in por:
        por[k].sort(key=lambda g: g["data"], reverse=True)
    return por


def grupo(g):
    return {"EST": "Estaduais", "BR": "Brasileirão", "SB": "Brasileirão"}.get(g["comp"], "Copas")


def imp(g):
    if g["tipo"] == "consolacao":
        return W["estadual"]
    c, k = g["comp"], ko(g)
    if c in ("EST", "NE", "PL"):
        if not k:
            return W["estadual"]
        if g["fase"] == "F" and g["tipo"] != "turno":
            return W["final_estadual"]
        return W["mata_mata_estadual"]
    if c == "BR":
        return W["brasileirao"]
    if c == "SB":
        return W["serie_b"]
    if c in ("SUP", "REC"):
        return W["supercopa"]
    if c in ("CB", "LIB", "SUL", "MUN"):  # Mundial de Clubes: mesmo peso dos mata-matas de copa
        if g["fase"] == "F":
            return W["final_copa"]
        if k:
            return W["mata_mata_copa"]
        return W["grupos_libertadores"] if c == "LIB" else W["grupos_sula"]
    raise ValueError(f"competição desconhecida: {g}")


def pts(g, team):
    my = g["gm"] if g["m"] == team else g["gv"]
    ot = g["gv"] if g["m"] == team else g["gm"]
    return 3 if my > ot else (1 if my == ot else 0)


def confrontos(games):
    kos = [g for g in sorted(games, key=lambda g: g["data"]) if ko(g)]
    ties = []
    for g in kos:
        key = (g["comp"], g["temp"], g["fase"], g["tipo"] == "turno")
        if ties:
            t = ties[-1]; last = t["jogos"][-1]
            gap = (dt.date.fromisoformat(g["data"]) - dt.date.fromisoformat(last["data"])).days
            if t["key"] == key and len(t["jogos"]) == 1 and not t["jogos"][0]["pen"] and gap <= (14 if g["comp"] == "EST" else 35):
                t["jogos"].append(g); continue
        ties.append(dict(key=key, jogos=[g]))
    for t in ties:
        agg = defaultdict(int)
        for g in t["jogos"]:
            agg[g["m"]] += g["gm"]; agg[g["v"]] += g["gv"]
        (a, ga), (b, gb) = list(agg.items())
        last = t["jogos"][-1]
        if ga != gb:
            w, como = (a if ga > gb else b), ("agregado" if len(t["jogos"]) > 1 else "jogo")
        elif last["pen"]:
            w, como = (last["m"] if last["pen"][0] > last["pen"][1] else last["v"]), "pênaltis"
        elif last["vantagem"]:
            w, como = last["vantagem"], ("gol fora" if "gol fora" in last["obs"] else "vantagem")
        else:
            w, como = None, "?"
        if any("STJD" in g["obs"] for g in t["jogos"]):  # volta não disputada por decisão do STJD
            como = "decisão do STJD"
        t.update(vencedor=w, como=como, fim=last["data"])
    return ties


def soma(team, gs, ts, filtro="Todas"):
    """gs: lista de (posição, jogo); ts: confrontos com 'pos'. Devolve num, den e contagens."""
    num = den = 0.0; n = v = e = d = cv = cl = 0
    for i, g in gs:
        if filtro == "Mata-mata" and not ko(g):
            continue
        if filtro in ("Estaduais", "Brasileirão", "Copas") and grupo(g) != filtro:
            continue
        w = REC[i // 10] * imp(g); p = pts(g, team)
        num += w * p; den += w * 3; n += 1; v += p == 3; e += p == 1; d += p == 0
    for t in ts:
        g = t["jogos"][-1]
        if filtro in ("Estaduais", "Brasileirão", "Copas") and grupo(g) != filtro:
            continue
        w = REC[t["pos"] // 10] * imp(g)
        num += w * (3 if t["vencedor"] == team else 0); den += w * 3
        cv += t["vencedor"] == team; cl += t["vencedor"] != team
    return num, den, n, v, e, d, cv, cl


def ix(num, den):
    return round(100 * num / den, 1) if den else None


def nivel(i):
    return "Freguesia" if i >= PESOS["limiar_freguesia"] else ("Vantagem clara" if i >= PESOS["limiar_vantagem"] else "Equilíbrio")


def br(d):
    return f"{d[8:]}/{d[5:7]}/{d[:4]}"


def comp_nome(g, uf):
    c = ESTNOME.get(uf, "Estadual") if g["comp"] == "EST" else COMPNOME[g["comp"]]
    fase = FASENOME.get(g["fase"], "") if ko(g) else ""
    if g["tipo"] == "turno": fase = FASENOME.get(g["fase"], "Mata-mata") + " de turno"
    if g["tipo"] == "consolacao": fase = "Taça Rio (consolação)"
    return f"{c} {g['temp']}" + (f" · {fase}" if fase else "")


def main(escopo, prefixo):
    """escopo: lista de clássicos (os 52 interestaduais ou os 66); prefixo: g12 ou g12c."""
    por = ler()
    ranking, indices, jogos, matamatas = [], [], [], []
    clubes = defaultdict(lambda: dict(num=0.0, den=0.0, v=0, e=0, d=0, mm_v=0, mm_d=0, conf=[]))
    for c in escopo:
        k, a, b = c["id"], c["time_a"], c["time_b"]
        games = por[k]
        if len(games) < N:
            raise SystemExit(f"{k}: só {len(games)} jogos na base")
        lab = f"{a} x {b}"
        gN = games[:N]; lim = gN[-1]["data"]
        allties = confrontos(games)
        ties = [dict(t) for t in allties if t["fim"] >= lim]
        if any(t["vencedor"] is None for t in ties):
            raise SystemExit(f"{k}: mata-mata sem vencedor: {[t['key'] for t in ties if t['vencedor'] is None]}")
        pos = {}
        for i, g in enumerate(gN):
            pos.setdefault(g["data"], i)
        for t in ties:
            t["pos"] = pos[t["fim"]]
        G = list(enumerate(gN))
        ra, rb = soma(a, G, ties), soma(b, G, ties)
        ia, ib = ix(ra[0], ra[1]), ix(rb[0], rb[1])
        dom, fre = (a, b) if ia >= ib else (b, a)
        r = ra if dom == a else rb
        # clubes: aproveitamento ponderado contra o G12, somando os 11 confrontos
        for team, rr, opp in ((a, ra, b), (b, rb, a)):
            cl = clubes[team]; cl["num"] += rr[0]; cl["den"] += rr[1]; cl["v"] += rr[3]; cl["e"] += rr[4]; cl["d"] += rr[5]
            cl["mm_v"] += rr[6]; cl["mm_d"] += rr[7]
            cl["conf"].append(dict(adversario=opp, indice=ix(rr[0], rr[1]), adv_indice=ix(*(rb if team == a else ra)[:2])))

        def sem_vencer(team):
            for n, g in enumerate(games):
                if pts(g, team) == 3:
                    return n, g["data"]
            return len(games), ""
        (ja, da), (jb, db) = sem_vencer(a), sem_vencer(b)
        jt, jn, jd = (a, ja, da) if ja >= jb else (b, jb, db)

        # recortes com peso (30/20/10) x filtro
        for J in JANELAS:
            gJ = G[:J]; limJ = gN[J - 1]["data"]; tJ = [t for t in ties if t["fim"] >= limJ]
            for f in FILTROS:
                sa, sb = soma(a, gJ, tJ, f), soma(b, gJ, tJ, f)
                if sa[2] == 0:
                    continue
                xa, xb = ix(sa[0], sa[1]), ix(sb[0], sb[1])
                top, ot, s = (a, b, sa) if (xa or 0) >= (xb or 0) else (b, a, sb)
                indices.append(dict(classico=lab, tipo=c["tipo"], filtro=f, janela=J, dominante=top, fregues=ot, indice=ix(s[0], s[1]),
                                    jogos=s[2], v=s[3], e=s[4], d=s[5], mm_dom=s[6], mm_fre=s[7], inicio=limJ,
                                    poucos="S" if s[2] < max(3, round(J * 0.12)) else "N", nivel=nivel(ix(s[0], s[1]))))
        # forma: últimos 5 (sem ranking)
        g5 = G[:5]; t5 = [t for t in ties if t["fim"] >= gN[4]["data"]]
        s5a, s5b = soma(a, g5, t5), soma(b, g5, t5)
        x5a, x5b = ix(s5a[0], s5a[1]), ix(s5b[0], s5b[1])
        f5t, f5 = (a, s5a) if x5a >= x5b else (b, s5b)
        # mando (30 jogos, sem neutros e sem o bônus dos mata-matas)
        mando = {}
        for casa in (a, b):
            gs = [(i, g) for i, g in G if g["m"] == casa and not g["neutro"]]
            s = soma(dom, gs, [])
            mando[casa] = dict(jogos=s[2], v=s[3], e=s[4], d=s[5], indice=ix(s[0], s[1]))
        neutros = sum(g["neutro"] for g in gN)
        vd = sum(t["vencedor"] == dom for t in ties)
        last = next((g for g in games if pts(g, fre) == 3), None)
        u = games[0]
        gd = sum(g["gm"] if g["m"] == dom else g["gv"] for g in gN); gf = sum(g["gv"] if g["m"] == dom else g["gm"] for g in gN)
        ranking.append(dict(classico=lab, id=k, tipo=c["tipo"], apelido=c.get("apelido", ""), time_a=a, time_b=b, dominante=dom, fregues=fre,
                            indice=ix(r[0], r[1]), indice_fregues=ix(*(rb if dom == a else ra)[:2]), nivel=nivel(ix(r[0], r[1])),
                            v=r[3], e=r[4], d=r[5], gols_dom=gd, gols_fre=gf, mata_matas=f"{vd} x {len(ties) - vd}", inicio=lim,
                            jejum_time=jt, jejum_jogos=jn, jejum_desde=jd,
                            jejum=next((n for n, g in enumerate(games) if pts(g, fre) == 3), len(games)),
                            ult_vit_fregues=(f"{br(last['data'])} {last['m']} {last['gm']}x{last['gv']} {last['v']}" if last else ""),
                            ultimo_jogo=f"{br(u['data'])} {u['m']} {u['gm']}x{u['gv']} {u['v']}",
                            forma_time=f5t, forma_indice=ix(f5[0], f5[1]), forma=f"{f5[3]}V {f5[4]}E {f5[5]}D",
                            casa_dom_jogos=mando[dom]["jogos"], casa_dom_indice=mando[dom]["indice"],
                            casa_dom=f"{mando[dom]['v']}V {mando[dom]['e']}E {mando[dom]['d']}D",
                            casa_fre_jogos=mando[fre]["jogos"], casa_fre_indice=mando[fre]["indice"],
                            casa_fre=f"{mando[fre]['v']}V {mando[fre]['e']}E {mando[fre]['d']}D", neutros=neutros))
        uf = c.get("uf", "")
        for i, g in enumerate(gN, 1):
            t = next((t for t in ties if t["fim"] == g["data"] and t["jogos"][-1] is g), None)
            jogos.append(dict(classico=lab, n=i, data=g["data"], mandante=g["m"], gm=g["gm"], gv=g["gv"], visitante=g["v"],
                              competicao=comp_nome(g, uf), categoria=grupo(g), mata_mata="S" if ko(g) else "N",
                              penaltis=f"{g['pen'][0]}-{g['pen'][1]}" if g["pen"] else "", neutro="S" if g["neutro"] else "",
                              classificado=t["vencedor"] if t else "", como=t["como"] if t else "",
                              peso=round(REC[(i - 1) // 10] * imp(g), 2), obs=g["obs"]))
        for t in sorted(ties, key=lambda t: t["fim"], reverse=True):
            g = t["jogos"][-1]
            placares = " / ".join(f"{x['m']} {x['gm']}x{x['gv']} {x['v']}" + (f" (pên. {x['pen'][0]}-{x['pen'][1]})" if x["pen"] else "") for x in t["jogos"])
            nome = comp_nome(g, uf)
            matamatas.append(dict(classico=lab, data=g["data"], competicao=nome.split(" · ")[0],
                                  fase=nome.split(" · ")[1] if " · " in nome else g["fase"], jogos=placares,
                                  avancou=t["vencedor"], como=t["como"], peso=round(REC[t["pos"] // 10] * imp(g), 2)))

    ranking.sort(key=lambda r: -r["indice"])
    for p, r in enumerate(ranking, 1):
        r["pos"] = p
    for f in FILTROS:
        for J in JANELAS:
            rs = [r for r in indices if r["filtro"] == f and r["janela"] == J]
            rs.sort(key=lambda r: (r["poucos"] == "S", -(r["indice"] or 0)))
            for p, r in enumerate(rs, 1):
                r["pos"] = p
    indices.sort(key=lambda r: (FILTROS.index(r["filtro"]), -r["janela"], r["pos"]))
    cl_rows = []
    for team, cl in clubes.items():
        conf = sorted(cl["conf"], key=lambda x: x["indice"] - x["adv_indice"])
        fregues_de = [x["adversario"] for x in conf if x["adv_indice"] >= PESOS["limiar_freguesia"]]
        desv = [x["adversario"] for x in conf if PESOS["limiar_vantagem"] <= x["adv_indice"] < PESOS["limiar_freguesia"]]
        domina = [x["adversario"] for x in conf[::-1] if x["indice"] >= PESOS["limiar_freguesia"]]
        vant = [x["adversario"] for x in conf[::-1] if PESOS["limiar_vantagem"] <= x["indice"] < PESOS["limiar_freguesia"]]
        cl_rows.append(dict(clube=team, indice=ix(cl["num"], cl["den"]), v=cl["v"], e=cl["e"], d=cl["d"],
                            mm=f"{cl['mm_v']} x {cl['mm_d']}", fregues_de=", ".join(fregues_de), desvantagem_contra=", ".join(desv),
                            domina=", ".join(domina), vantagem_sobre=", ".join(vant),
                            pior=conf[0]["adversario"], melhor=conf[-1]["adversario"]))
    cl_rows.sort(key=lambda r: -r["indice"])
    for p, r in enumerate(cl_rows, 1):
        r["pos"] = p
    meta = dict(atualizado=dt.date.today().isoformat(), ultimo_jogo=max(g["data"] for v in por.values() for g in v), janela=N,
                confrontos=len(ranking))
    os.makedirs(P("data"), exist_ok=True); os.makedirs(P("csv"), exist_ok=True)
    for nome, rows in (("ranking", ranking), ("indices", indices), ("jogos", jogos), ("matamatas", matamatas), ("clubes", cl_rows)):
        json.dump(rows, open(P("data", f"{prefixo}_{nome}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        cols = (["pos"] + [x for x in rows[0] if x != "pos"]) if "pos" in rows[0] else list(rows[0].keys())
        with open(P("csv", f"{prefixo}_{nome}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    json.dump(meta, open(P("data", f"{prefixo}_meta.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"== {prefixo}: {len(ranking)} confrontos")
    for r in ranking[:5]:
        print(f"{r['pos']}. {r['classico']}: {r['dominante']} {r['indice']} ({r['nivel']})")
    print("Clubes:", ", ".join(f"{r['clube']} {r['indice']}" for r in cl_rows))


if __name__ == "__main__":
    main([c for c in CLASSICOS if c["tipo"] == "Interestadual"], "g12")   # aba G12: só os 52 interestaduais
    main(CLASSICOS, "g12c")                                              # aba G12 com clássicos: os 66
