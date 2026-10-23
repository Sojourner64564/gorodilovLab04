import pandas as pd


cols = [
    "State", "Area code", "International plan", "Number vmail messages",
    "Total day minutes", "Total day calls",
    "Total eve minutes", "Total eve calls",
    "Total night minutes", "Total night calls",
    "Customer service calls", "Churn",
]
df = pd.read_csv("telecom_churn.csv", usecols=cols)

# 1. Общая информация, пропуски
df.info()
print(df.describe())
print("\nПропусков по столбцам:")
print(df.isna().sum())
print("Всего пропусков:", df.isna().sum().sum())

# 2. Активные / потерянные клиенты
print("\nЧисло клиентов (False - активен, True - потерян):")
print(df["Churn"].value_counts())
print("\nДоля клиентов, %:")
print((df["Churn"].value_counts(normalize=True) * 100).round(2))

# 3. Средняя продолжительность одного звонка
total_minutes = (df["Total day minutes"] + df["Total eve minutes"]
                 + df["Total night minutes"])
total_calls = (df["Total day calls"] + df["Total eve calls"]
               + df["Total night calls"])
df["Mean call duration"] = total_minutes / total_calls

print("\nТоп-10 по средней продолжительности звонка:")
print(df.sort_values("Mean call duration", ascending=False).head(10))

# 4. Средняя продолжительность звонка по Churn
print("\nСредняя продолжительность звонка по Churn:")
print(df.groupby("Churn")["Mean call duration"].mean())

# 5. Среднее число звонков в поддержку по Churn
print("\nСреднее число звонков в поддержку по Churn:")
print(df.groupby("Churn")["Customer service calls"].mean())

# 6. Таблица сопряженности Churn / Customer service calls
ct_calls = pd.crosstab(df["Customer service calls"], df["Churn"])
ct_calls["Churn, %"] = (ct_calls[True] / (ct_calls[False] + ct_calls[True])
                        * 100).round(1)
print("\nCustomer service calls vs Churn:")
print(ct_calls)
print("Средний отток по всему датафрейму, %:",
      round(df["Churn"].mean() * 100, 1))
print("Число звонков с оттоком > 40%:",
      list(ct_calls.index[ct_calls["Churn, %"] > 40]))

# 7. Таблица сопряженности Churn / International plan
ct_intl = pd.crosstab(df["International plan"], df["Churn"])
ct_intl["Churn, %"] = (ct_intl[True] / (ct_intl[False] + ct_intl[True])
                       * 100).round(1)
print("\nInternational plan vs Churn:")
print(ct_intl)

# 8. Прогнозируемый отток и ошибки I и II рода

# Правило: отток прогнозируем, если клиент звонил в поддержку 4 и более раз
# ИЛИ у него подключен международный роуминг (отток в этих группах > 40%).
df["Прогнозируемый отток"] = (
    (df["Customer service calls"] >= 4) | (df["International plan"] == "Yes")
)

print("\nМатрица ошибок (строки - Churn, столбцы - прогноз):")
print(pd.crosstab(df["Churn"], df["Прогнозируемый отток"]))

fp = ((df["Прогнозируемый отток"]) & (~df["Churn"])).sum()  # ошибка I рода
fn = ((~df["Прогнозируемый отток"]) & (df["Churn"])).sum()  # ошибка II рода
n_active = (~df["Churn"]).sum()
n_lost = df["Churn"].sum()
n = len(df)

print(f"\nОшибки I рода (ложноположительные): {fp}")
print(f"  {fp / n_active * 100:.1f}% от активных клиентов, "
      f"{fp / n * 100:.1f}% от всех клиентов")
print(f"Ошибки II рода (ложноотрицательные): {fn}")
print(f"  {fn / n_lost * 100:.1f}% от потерянных клиентов, "
      f"{fn / n * 100:.1f}% от всех клиентов")
print(f"Общая доля ошибок: {(fp + fn) / n * 100:.1f}%")