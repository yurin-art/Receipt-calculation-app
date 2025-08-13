import streamlit as st
import pandas as pd
from datetime import datetime

st.title("金額組み合わせ最適化システム")

# --- セッション状態の初期化 ---
if "item_list" not in st.session_state:
    st.session_state.item_list = []

if "results_history" not in st.session_state:
    st.session_state.results_history = []  # セッションのみ保持

# --- 上限金額の入力 ---
limit = st.number_input("上限金額（円）", min_value=1, value=40000, step=1000)

# --- 金額とラベル入力 ---
st.write("金額とラベルを入力してください")
label = st.text_input("ラベル（例: 商品A）")
amount = st.number_input("金額", min_value=1, step=1)

if st.button("追加"):
    if label and amount > 0:
        st.session_state.item_list.append((label, int(amount)))
        st.success(f"{label} ({amount}円) を追加しました")
    else:
        st.error("ラベルと金額を正しく入力してください")

# --- 入力済みデータの表示 ---
if st.session_state.item_list:
    df_items = pd.DataFrame(st.session_state.item_list, columns=["ラベル", "金額"])
    st.subheader("入力データ")
    st.table(df_items)

# --- 計算処理 ---
if st.button("計算開始") and st.session_state.item_list:
    items = st.session_state.item_list
    n = len(items)
    dp = [[0] * (limit + 1) for _ in range(n + 1)]
    
    # DP計算
    for i in range(1, n + 1):
        label_i, amount_i = items[i - 1]
        for w in range(limit + 1):
            if amount_i <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-amount_i] + amount_i)
            else:
                dp[i][w] = dp[i-1][w]
    
    best_sum = dp[n][limit]
    
    # 逆追跡
    w = limit
    chosen = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            chosen.append(items[i-1])
            w -= items[i-1][1]
    
    df_chosen = pd.DataFrame(chosen, columns=["ラベル", "金額"])
    df_chosen = df_chosen.sort_values(by="金額", ascending=False).reset_index(drop=True)

    st.subheader("今回の最適な組み合わせ")
    st.table(df_chosen)
    st.write(f"合計金額: {best_sum}円")
    st.write(f"残額: {limit - best_sum}円")

    # --- 履歴に追加 ---
    st.session_state.results_history.append({
        "日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "上限金額": limit,
        "合計金額": best_sum,
        "残額": limit - best_sum,
        "組み合わせ": df_chosen
    })

# --- 履歴の表示 ---
if st.session_state.results_history:
    st.subheader("過去の計算結果履歴")

    # 全削除ボタン
    if st.button("履歴を全削除"):
        st.session_state.results_history = []
        st.success("履歴を全削除しました")

    # 各履歴表示と個別削除
    for idx, record in enumerate(st.session_state.results_history, start=1):
        st.markdown(f"**{idx}. {record['日時']} - 上限 {record['上限金額']}円 / 合計 {record['合計金額']}円 / 残額 {record['残額']}円**")
        st.table(record["組み合わせ"])
        if st.button(f"この履歴を削除 {idx}"):
            st.session_state.results_history.pop(idx-1)
            st.experimental_rerun()

    # 全履歴ダウンロード
    all_history = []
    for rec in st.session_state.results_history:
        df_temp = rec["組み合わせ"].copy()
        df_temp["日時"] = rec["日時"]
        df_temp["上限金額"] = rec["上限金額"]
        df_temp["合計金額"] = rec["合計金額"]
        df_temp["残額"] = rec["残額"]
        all_history.append(df_temp)
    df_all = pd.concat(all_history, ignore_index=True)
    csv_data = df_all.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="履歴をCSVでダウンロード",
        data=csv_data,
        file_name="results_history.csv",
        mime="text/csv"
    )
