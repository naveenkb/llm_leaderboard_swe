import pandas as pd

file = 'llm_leaderboard_data.csv'

df = pd.read_csv(file)
df.columns = ["family", "model", "score", "date", "benchmark_date", "benchmark"]

# Convert to datetime
df["date"] = pd.to_datetime(df["date"])
df["benchmark_date"] = pd.to_datetime(df["benchmark_date"])

df["score"] = df["score"].str.replace('%', '', regex=False).astype(float)



df_base = df[df.benchmark == 'swe-bench']
df_verified = df[df.benchmark == 'swe-bench-verified']
df_verified = df_verified[df_verified.benchmark_date <= "2025-09-20"]
df_pro = df[df.benchmark == 'swe-bench-pro']

timeline_base = pd.date_range(
    start=df_base["benchmark_date"].min(),
    end=df_base["benchmark_date"].max(),
    freq="W"
)
timeline_base = timeline_base.union(pd.DatetimeIndex(df_base.benchmark_date.unique()))

timeline_verified = pd.date_range(
    start=df_verified["benchmark_date"].min(),
    end=df_verified["benchmark_date"].max(),
    freq="W"
)
timeline_verified = timeline_verified.union(pd.DatetimeIndex(df_verified.benchmark_date.unique()))

timeline_pro = pd.date_range(
    start=df_pro["benchmark_date"].min(),
    end=df_pro["benchmark_date"].max(),
    freq="W"
)
timeline_pro = timeline_pro.union(pd.DatetimeIndex(df_pro.benchmark_date.unique()))


df_base_new = df_base.groupby(['benchmark_date', 'family']).max('score').reset_index()

df_verified_new = df_verified.groupby(['benchmark_date', 'family']).max('score').reset_index()

df_pro_new = df_pro.groupby(['benchmark_date', 'family']).max('score').reset_index()


pivot_scores_base = (
    df_base_new.pivot(index="benchmark_date", columns="family", values="score")
      .reindex(timeline_base)
      .ffill()
)

pivot_scores_verified = (
    df_verified_new.pivot(index="benchmark_date", columns="family", values="score")
      .reindex(timeline_verified)
      .ffill()
)

pivot_scores_pro = (
    df_pro_new.pivot(index="benchmark_date", columns="family", values="score")
      .reindex(timeline_pro)
      .ffill()
)

pivot_scores_base_max = pivot_scores_base.cummax()
pivot_scores_verified_max = pivot_scores_verified.cummax()
pivot_scores_pro_max = pivot_scores_pro.cummax()

pivot_scores_max = pd.concat([pivot_scores_base_max, pivot_scores_verified_max, pivot_scores_pro_max], axis=0)


pivot_scores_max.T.to_csv('pivot_scores_all.csv', index=True)