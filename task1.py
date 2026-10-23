import pandas as pd
import matplotlib.pyplot as plt

# 1. Загрузка данных
df = pd.read_csv("athlete_events.csv")

# 2. Количество значений по каждому признаку и пропуски
print("\n--- Количество непустых значений ---")
print(df.count())

missing = df.isna().sum()
print("\n--- Количество пропусков ---")
print(missing[missing > 0].sort_values(ascending=False))
print("Больше всего пропусков в признаке:", missing.idxmax())


# 3. Статистика по возрасту, росту и весу
print("\n--- describe ---")
print(df[["Age", "Height", "Weight"]].describe())

# 4. Вопросы
# 4.1 Самый молодой участник ОИ 1992 года
d1992 = df[df["Year"] == 1992]
min_age = d1992["Age"].min()
youngest = d1992[d1992["Age"] == min_age]
print(f"\n4.1 Возраст самого молодого участника 1992 года: {min_age}")
print(youngest[["Name", "Age", "Sport", "Event"]].to_string(index=False))

# 4.2 Все виды спорта, когда-либо входившие в программу ОИ
sports = df["Sport"].unique()
print(sorted(sports))

# 4.3 Средний рост теннисисток на ОИ 2000 года
tennis_w = df[(df["Sex"] == "F") & (df["Sport"] == "Tennis") & (df["Year"] == 2000)]
mean_height = tennis_w.drop_duplicates(subset="ID")["Height"].mean()
print(f"\n4.3 Средний рост теннисисток в 2000 году: {mean_height:.2f} см")

# 4.4 Золотые медали Китая в настольном теннисе на ОИ 2008
tt = df[
    (df["Sport"] == "Table Tennis")
    & (df["Year"] == 2008)
    & (df["NOC"] == "CHN")
    & (df["Medal"] == "Gold")
]

gold_count = tt["Event"].nunique()
print(f"\n4.4 Золотых медалей Китая в настольном теннисе в 2008: {gold_count}")
print(f"(Для справки: строк с золотом, т.е. награждённых спортсменов: {len(tt)})")

# 4.5 Изменение числа видов спорта на летних ОИ 2004 vs 1988
summer = df[df["Season"] == "Summer"]
n_1988 = summer[summer["Year"] == 1988]["Sport"].nunique()
n_2004 = summer[summer["Year"] == 2004]["Sport"].nunique()
print(f"\n4.5 Видов спорта: 1988 — {n_1988}, 2004 — {n_2004}, "
      f"изменение: {n_2004 - n_1988:+d}")

# 4.6 Гистограмма возраста мужчин-керлингистов на ОИ 2014
curling = df[
    (df["Sport"] == "Curling") & (df["Sex"] == "M") & (df["Year"] == 2014)
]
plt.figure(figsize=(8, 5))
plt.hist(curling["Age"].dropna())
plt.title("Возраст мужчин-керлингистов, ОИ 2014")
plt.xlabel("Возраст")
plt.ylabel("Количество спортсменов")
plt.show()

# 4.7 Зимняя олимпиада 2006: медали и средний возраст по странам
winter2006 = df[(df["Year"] == 2006) & (df["Season"] == "Winter")]
by_country = winter2006.groupby("NOC").agg(
    Medals=("Medal", "count"),   # count считает только непустые значения
    MeanAge=("Age", "mean"),
)
by_country = by_country[by_country["Medals"] > 0]
print("\n4.7 Медали и средний возраст по странам (Турин-2006):")
print(by_country.sort_values("Medals", ascending=False))

# 4.8 Сводная таблица: медали по достоинству для каждой страны
medalists = winter2006.dropna(subset=["Medal"])
pivot = medalists.pivot_table(
    index="NOC",
    columns="Medal",
    values="ID",
    aggfunc="count",
    fill_value=0,
)
pivot = pivot[["Gold", "Silver", "Bronze"]]  # порядок по достоинству
print("\n4.8 Сводная таблица медалей (Турин-2006):")
print(pivot)