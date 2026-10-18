"""Klassifikation (1=hoch, 2=mittel, 3=niedrig, 0=ohne) und Zusammenhang."""
import heapq

import h3
import mapclassify
import numpy as np


def classify(cells, cfg, method):
    cells = cells.copy()
    pos = cells["dens"] > 0
    y = cells.loc[pos, "dens"].to_numpy()
    cls = np.zeros(len(cells), int)
    if method == "jenks":
        np.random.seed(cfg["random_seed"])
        cls[pos.to_numpy()] = 3 - mapclassify.NaturalBreaks(y, k=3).yb
    elif method == "quantile":
        t = np.quantile(y, cfg["quantiles"])
        cls[pos.to_numpy()] = np.select([y >= t[2], y >= t[1], y >= t[0]], [1, 2, 3], 0)
    elif method == "peak_share":
        t = np.asarray(cfg["peak_share"]) * y.max()
        cls[pos.to_numpy()] = np.select([y >= t[0], y >= t[1], y >= t[2]], [1, 2, 3], 0)
    elif method == "equal_area":
        cls = _equal_area(cells, pos, cfg["equal_area_ha"])
    else:
        raise ValueError(f"unbekannte Klassifikation: {method}")
    cells["cls"] = cls
    return cells


def _equal_area(cells, pos, targets):
    """Ab der Maximalzelle zusammenhängend nach Dichte auffüllen bis zu den kumulativen Zielflächen."""
    idx = {c: i for i, c in enumerate(cells["h3"])}
    dens, area, ok = cells["dens"].to_numpy(), cells["area_ha"].to_numpy(), pos.to_numpy()
    cls = np.zeros(len(cells), int)
    start = int(np.argmax(dens))
    heap, seen, cum, stage = [(-dens[start], start)], {start}, 0.0, 0
    while heap:
        _, i = heapq.heappop(heap)
        while stage < 3 and cum + area[i] / 2 > targets[stage]:  # nächstliegend: Abweichung ≤ ½ Zelle
            stage += 1
        if stage == 3:
            break
        cls[i], cum = stage + 1, cum + area[i]
        for n in h3.grid_disk(cells["h3"].iat[i], 1):
            j = idx.get(n)
            if j is not None and ok[j] and j not in seen:
                seen.add(j)
                heapq.heappush(heap, (-dens[j], j))
    return cls


def component(seed, members):
    """Zusammenhangskomponente (H3-Nachbarschaft) von seed innerhalb members."""
    if seed not in members:
        return set()
    comp, todo = {seed}, [seed]
    while todo:
        for n in h3.grid_disk(todo.pop(), 1):
            if n in members and n not in comp:
                comp.add(n)
                todo.append(n)
    return comp


def limit_area(cells, max_ha):
    """Zonen größer als max_ha auf die dichtesten zusammenhängenden Zellen kürzen (Wachstum ab Maximalzelle bzw.
    ab der Grenze zur vorigen Zone). Abgeschnittene Zellen gehen an die nächste Zone, nach Z3 an keine."""
    cells = cells.copy()
    idx = {c: i for i, c in enumerate(cells["h3"])}
    zone, dens, area = cells["zone"].to_numpy().copy(), cells["dens"].to_numpy(), cells["area_ha"].to_numpy()
    nbrs = lambda i: (idx[n] for n in h3.grid_disk(cells["h3"].iat[i], 1) if n in idx and idx[n] != i)
    prev, carry = set(), set()
    for z, limit in zip((1, 2, 3), max_ha):
        members = set(np.flatnonzero(zone == z)) | carry
        keep = members
        if area[list(members)].sum() > limit:
            seeds = {i for i in members if any(n in prev for n in nbrs(i))} or {max(members, key=lambda i: dens[i])}
            heap, seen, keep, cum = [(-dens[i], i) for i in seeds], set(seeds), set(), 0.0
            heapq.heapify(heap)
            while heap:
                _, i = heapq.heappop(heap)
                if cum + area[i] > limit:
                    continue
                keep.add(i)
                cum += area[i]
                for n in nbrs(i):
                    if n in members and n not in seen:
                        seen.add(n)
                        heapq.heappush(heap, (-dens[n], n))
        carry = members - keep
        zone[list(carry)] = 0
        zone[list(keep)] = z
        prev |= keep
    cells["zone"] = zone
    return cells


def assign_zones(cells):
    """zone 1..3 nach Zusammenhang mit der Maximalzelle; klassifizierte Rest-Zellen = Inseln (zone 0)."""
    cells = cells.copy()
    seed = cells.loc[cells["dens"].idxmax(), "h3"]
    by = lambda m: set(cells.loc[m, "h3"])
    z1 = component(seed, by(cells["cls"] == 1))
    z2 = component(seed, by(cells["cls"].isin([1, 2]))) - z1
    z3 = component(seed, by(cells["cls"] > 0)) - z1 - z2
    cells["zone"] = [1 if c in z1 else 2 if c in z2 else 3 if c in z3 else 0 for c in cells["h3"]]
    islands = cells[(cells["cls"] > 0) & (cells["zone"] == 0)]
    return cells, islands
