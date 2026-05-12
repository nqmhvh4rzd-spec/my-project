import urllib.request
import json
from datetime import datetime
import ctypes

# ===== 銘柄リスト =====
STOCKS = [
    ("9986", "蔵王産業"),
    ("3076", "あいHD"),
    ("8130", "サンゲツ"),
    ("3333", "あおぞら"),
    ("4008", "住友精化"),
    ("4042", "東ソー"),
    ("8309", "三井住友トラストグループ"),
    ("8725", "MS&ADインシュアランスグループHD"),
    ("8593", "三菱HCキャピタル"),
    ("8584", "ジャックス"),
    ("7723", "愛知時計電機"),
    ("3231", "野村不動産HD"),
    ("3003", "ヒューリック"),
    ("2169", "CDS"),
    ("6073", "アサンテ"),
    ("9769", "学究社"),
    ("4641", "アルプス技研"),
    ("3817", "SRAホールディングス"),
    ("4832", "JFEシステムズ"),
    ("4719", "アルファシステムズ"),
    ("2003", "日東富士製粉"),
    ("1414", "ショーボンドホールディングス"),
    ("1928", "積水ハウス"),
    ("6432", "竹内製作所"),
    ("6345", "アイチコーポレーション"),
    ("9381", "エーアイテイー"),
    ("5388", "クニミネ工業"),
    ("7989", "立川ブラインド工業"),
    ("7820", "ニホンフラッシュ"),
    ("7994", "オカムラ"),
    ("4540", "ツムラ"),
    ("9513", "電源開発"),
    ("1343", "NF・J-REIT ETF"),
]

THRESHOLD = 0.10  # ±10%

def get_price(code):
    """stooqから株価を取得（当日・前日）"""
    url = f"https://stooq.com/q/d/l/?s={code}.jp&i=d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            lines = res.read().decode("utf-8").strip().split("\n")
        if len(lines) < 3:
            return None, None
        # 最新2行を取得
        latest = lines[-1].split(",")
        prev = lines[-2].split(",")
        return float(latest[4]), float(prev[4])  # Close価格
    except Exception:
        return None, None

def show_popup(title, message):
    """Windowsポップアップ通知"""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*50}")
    print(f"  高配当株 ±10%監視  {now}")
    print(f"{'='*50}")

    alerts = []
    errors = []

    for code, name in STOCKS:
        today, prev = get_price(code)
        if today is None or prev is None:
            errors.append(f"{name}({code}): 取得失敗")
            print(f"  ✗ {name}({code}): 取得失敗")
            continue

        change = (today - prev) / prev
        sign = "▲" if change >= 0 else "▼"
        pct = abs(change) * 100
        print(f"  {sign}{pct:.2f}%  {name}({code})  {prev:.0f}→{today:.0f}円")

        if abs(change) >= THRESHOLD:
            direction = "急騰" if change > 0 else "急落"
            alerts.append(f"【{direction}】{name}({code}): {sign}{pct:.2f}% ({prev:.0f}→{today:.0f}円)")

    print(f"\n{'='*50}")
    if alerts:
        print("⚠️  アラート銘柄:")
        for a in alerts:
            print(f"  {a}")
        popup_msg = "\n".join(alerts)
        show_popup("株価アラート ±10%超え", popup_msg)
    else:
        print("✅ 全銘柄±10%以内（異常なし）")

    if errors:
        print(f"\n取得失敗: {len(errors)}件")
        for e in errors:
            print(f"  {e}")

    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
