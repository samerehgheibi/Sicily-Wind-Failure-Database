import pandas as pd
import numpy as np

# مسیرها را ویرایش کن
inp_path = r"C:\Users\samer\OneDrive\Desktop\thesis\ماکزیمم و مینیمم سرعت باد\per_way_node_day_wind_minmax.csv"
out_path = r"C:\Users\samer\OneDrive\Desktop\thesis\ماکزیمم و مینیمم سرعت باد\per_way_node_day_wind_minmax_failures_one_node_per_year_no_repeat.csv"

THRESH = 15.0
RNG_SEED = 9876
rng = np.random.default_rng(RNG_SEED)

df = pd.read_csv(inp_path)

def find_col(df, cands):
    for c in cands:
        if c in df.columns:
            return c
    for col in df.columns:
        cl = col.lower()
        for c in cands:
            if c in cl:
                return col
    return None

date_col = find_col(df, ["date","day","datetime","timestamp"])
wind_col = find_col(df, ["wind_speed","wind_max","max_wind","wind","ws","speed"])
v_id_col = find_col(df, ["v_id","vid"])
way_col = find_col(df, ["way_id","way"])
node_col = find_col(df, ["node_id","node"])

main_id = v_id_col if v_id_col else (way_col if way_col else None)
if main_id is None:
    for c in df.columns:
        if any(k in c.lower() for k in ["v_id","way_id","vid","way","id"]):
            main_id = c
            break

if date_col is None or wind_col is None or node_col is None or main_id is None:
    raise ValueError("ستون‌های کلیدی پیدا نشد. نام ستون‌ها را بررسی کن.")

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df[wind_col] = pd.to_numeric(df[wind_col], errors="coerce")
df["year"] = df[date_col].dt.year
df["failure"] = 0

def priority_series(s):
    pr = pd.Series(0, index=s.index, dtype=int)
    pr[s >= 21] = 3
    pr[(s >= 20) & (s < 21)] = 2
    pr[(s >= 19) & (s < 20)] = 1
    return pr

def top_two_days_for_node(sub):
    sub = sub.copy()
    sub["__day__"] = sub[date_col].dt.normalize()
    sub["__prio__"] = priority_series(sub[wind_col])
    sub = sub.sort_values(["__prio__", wind_col, date_col], ascending=[False, False, True])
    best_per_day = sub.groupby("__day__", as_index=False).head(1)
    if best_per_day["__day__"].nunique() < 2:
        return []
    best_per_day = best_per_day.sort_values(["__prio__", wind_col, date_col], ascending=[False, False, True])
    return best_per_day.head(2).index.tolist()

def score_picks(df_node, idxs):
    winds = df_node.loc[idxs, wind_col]
    return (
        int((winds >= 21).sum()),
        int(((winds >= 20) & (winds < 21)).sum()),
        int(((winds >= 19) & (winds < 20)).sum()),
        float(winds.sum()),
    )

selected_indices = []

# پردازش به ازای هر v_id و به ترتیب سال‌ها
for vid, sub_all in df.groupby(main_id):
    years = sorted([y for y in sub_all["year"].dropna().unique()])
    prev_node = None
    for yr in years:
        grp = sub_all[sub_all["year"] == yr]
        eligible = grp[(grp[wind_col] > THRESH) & (~grp[date_col].isna())].copy()
        if eligible.empty:
            prev_node = None
            continue

        candidates = []
        for nid, node_df in eligible.groupby(node_col):
            picks = top_two_days_for_node(node_df)
            if len(picks) == 2:
                score = score_picks(node_df, picks)
                candidates.append((score, nid, picks, node_df))

        if not candidates:
            prev_node = None
            continue

        # الزام تفاوت نود نسبت به سال قبل
        if prev_node is not None:
            candidates_diff = [c for c in candidates if c[1] != prev_node]
        else:
            candidates_diff = candidates

        chosen = None
        if candidates_diff:
            max_score = max(c[0] for c in candidates_diff)
            best = [c for c in candidates_diff if c[0] == max_score]
            chosen = best[rng.integers(0, len(best))] if len(best) > 1 else best[0]
        else:
            chosen = None  # هیچ نود متفاوتی موجود نیست -> این سال برچسب نمی‌خورد

        if chosen is not None:
            selected_indices.extend(chosen[2])
            prev_node = chosen[1]
        else:
            prev_node = None

df["failure"] = 0
df.loc[selected_indices, "failure"] = 1
df.to_csv(out_path, index=False)
print("Saved:", out_path)
