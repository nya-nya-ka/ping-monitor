# Network Monitor (Ping RTT & Packet Loss Monitor)

Pingを用いてネットワークの通信状態をリアルタイムで監視するアプリケーションです。  
RTTとPacket Lossの値を継続的に取得し、グラフとして可視化します。

FastAPIをバックエンドとして使用し、Chart.jsをフロントエンドに使用してグラフを描画します。

---

# 概要

本アプリケーションは、指定したホストに対して定期的にPingを実行し、

- RTT（往復遅延時間）
- Packet Loss（パケット損失率）

を取得してデータベースに保存し、リアルタイムに画面に表示します。

また、通信状態の異常を自動検知し、ユーザーに知らせます。

---

# 主な機能

## 定期Ping監視

GoogleとYahooの2つのホストに対して定期的にPingを実行します。

### 監視対象

- google.com  
- yahoo.co.jp

---

## ホスト切り替え

画面右上のセレクタから表示するグラフを切り替えることができます。

---

## RTT / Packet Loss グラフ表示

以下の値を時系列グラフとして表示します。

- RTT (ms)
- Packet Loss (%)

---

## 異常検知機能

以下の条件を満たした場合、通信異常として検知します。

| 状態 | 条件 |
|-----|-----|
| 正常 | RTT 50ms以下 |
| 軽微な遅延 | 100〜200ms |
| 高遅延 | 200ms以上 |
| 通信異常 | Packet Loss > 0 または Timeout |

異常が発生すると、RTTのグラフ線が **赤色** になります。

---

## 時間範囲スライダー

グラフの表示範囲をスライダーで操作できます。

また、画面上部には

- RTTの現在値
- Packet Lossの現在値

が表示されます。

---

# 使用技術

## Backend

- Python  
- FastAPI  
- SQLite  
- subprocess（Ping実行）  
- threading（バックグラウンド監視）

---

## Frontend

- HTML  
- CSS  
- JavaScript  
- Chart.js  
- chartjs-adapter-date-fns
