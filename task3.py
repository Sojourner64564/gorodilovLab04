import re
from io import StringIO
from urllib.request import Request, urlopen

import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

URL = "https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions"

# 1. Загрузка таблицы чемпионов по сезонам
req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(req).read().decode("utf-8")

tables = pd.read_html(StringIO(html), match="Fastest laps")
raw = max(tables, key=len)

# 2. Просмотр результата и очистка
print(raw.head())
print(raw.tail())

raw.columns = [
    re.sub(r"\[.*?\]", "", str(c[-1] if isinstance(c, tuple) else c)).strip()
    for c in raw.columns
]
print(list(raw.columns))

df = raw[raw["Season"].astype(str).str.fullmatch(r"\d{4}")].copy()

df = df.drop_duplicates(subset="Season", keep="first").reset_index(drop=True)

print("\nТипы данных до преобразования:")
print(df.dtypes)

# 3. Преобразование к числовому типу
def to_num(series):
    return pd.to_numeric(series.astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0])


int_cols = ["Season", "Age", "Poles", "Wins", "Podiums", "Fastest laps",
            "# of rounds remaining"]
float_cols = ["Points", "% Points", "Margin", "% Margin"]

for col in int_cols:
    df[col] = to_num(df[col]).astype("int64")
for col in float_cols:
    df[col] = to_num(df[col])

df["Rounds"] = df["Clinched"].str.extract(r"of\s+(\d+)")[0].astype("int64")

country = r"^(?:[A-Z]{2,3}|Brazil|Austria)\s+"
df["Driver"] = df["Driver"].str.replace(country, "", regex=True).str.strip()
df["Chassis"] = df["Chassis"].str.replace(country, "", regex=True).str.strip()

print("\nТипы данных после преобразования:")
print(df.dtypes)
print(df[["Season", "Driver", "Age", "Chassis", "Wins", "Rounds"]].head(10))

# 4. Вопросы

# 4.1 Возраст чемпионов: средний, минимальный, максимальный
print("\n4.1 Возраст чемпионов")
print(f"Средний: {df['Age'].mean():.2f}")
youngest = df.loc[df["Age"].idxmin()]
oldest = df.loc[df["Age"].idxmax()]
print(f"Минимальный: {youngest['Age']} ({youngest['Driver']}, {youngest['Season']})")
print(f"Максимальный: {oldest['Age']} ({oldest['Driver']}, {oldest['Season']})")
print("Все гонщики с минимальным возрастом:")
print(df.loc[df["Age"] == df["Age"].min(), ["Season", "Driver", "Age"]])

# 4.2 Команда (конструктор шасси) с наибольшим числом личных титулов
print("\n4.2 Титулы по конструкторам шасси")
by_constructor = df["Chassis"].value_counts()
print(by_constructor)
best = by_constructor[by_constructor == by_constructor.max()]
print("Больше всего титулов у:", ", ".join(best.index), f"({best.iloc[0]})")

# 4.3 Гонщики с наибольшим числом чемпионских титулов
print("\n4.3 Титулы по гонщикам")
by_driver = df["Driver"].value_counts()
print(by_driver.head(10))
top = by_driver[by_driver == by_driver.max()]
print("Больше всего титулов:", ", ".join(top.index), f"({top.iloc[0]})")

# 4.4 Чемпионы, выигравшие менее 30% гонок сезона
df["Win share"] = df["Wins"] / df["Rounds"]
low = df[df["Win share"] < 0.3]
print("\n4.4 Чемпионы, выигравшие менее 30% гонок сезона")
print(low[["Season", "Driver", "Wins", "Rounds", "Win share"]]
      .assign(**{"Win share": lambda t: (t["Win share"] * 100).round(1)})
      .rename(columns={"Win share": "Win share, %"}))

# 4.5 Максимальный перерыв между двумя последовательными титулами
print("\n4.5 Перерывы между последовательными титулами")
gaps = []
for driver, seasons in df.groupby("Driver")["Season"]:
    years = sorted(seasons)
    for a, b in zip(years, years[1:]):
        gaps.append((b - a, driver, a, b))

gaps.sort(reverse=True)
max_gap = gaps[0][0]
for gap, driver, a, b in gaps:
    if gap == max_gap:
        print(f"Максимальный перерыв: {gap} лет, {driver} ({a} -> {b})")
print("Топ-5 перерывов:")
for gap, driver, a, b in gaps[:5]:
    print(f"  {driver}: {a} -> {b}, {gap} лет")