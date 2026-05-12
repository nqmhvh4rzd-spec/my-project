import urllib.request
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
 
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
 
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")
NOTIFY_ADDRESS = os.environ.get("NOTIFY_ADDRESS", "")
 
def get_price(code):
    url = f"https://stooq.com/q/d/l/?s={code}.jp&i=d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            lines = res.read().decode("utf-8").strip().split("\n")
        if len(lines) < 3:
            return None, None
        latest = lines[-1].split(",")
        prev = lines[-2].split(",")
        return float(latest[4]), float(prev[4])
    except Exception:
        return None, None
 
def send_email(subject, body):
    if not GMAIL_ADDRESS or not GMAIL_PASSWORD or not NOTIFY_ADDRESS:
        print("メール設定が不足しています")
        return
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = NOTIFY_ADDRESS
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        print("メール送信完了")
    except Exception as e:
        print(f"メール送信失敗: {e}")
 
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*50}")
    print(f"  高配当株 ±10%監視  {now}")
    print(f"{'='*50}")
 
    alerts = []
    results = []
    errors = []
 
    for code, name in STOCKS:
        today, prev = get_price(code)
        if today is None or prev is None:
            errors.append(f"{name}({code}): 取得失敗")
            print(f"  x {name}({code}): 取得失敗")
            continue
 
        change = (today - prev) / prev
        sign = "▲" if change >= 0 else "▼"
        pct = abs(change) * 100
        line = f"  {sign}{pct:.2f}%  {name}({code})  {prev:.0f}→{today:.0f}円"
        print(line)
        results.append(line)
 
        if abs(change) >= THRESHOLD:
            direction = "急騰" if change > 0 else "急落"
            alerts.append(f"【{direction}】{name}({code}): {sign}{pct:.2f}% ({prev:.0f}→{today:.0f}円)")
 
    print(f"\n{'='*50}")
 
    if alerts:
        print("アラート銘柄:")
        for a in alerts:
            print(f"  {a}")
        subject = f"【株価アラート】±10%超え {len(alerts)}銘柄 {now}"
        body = "以下の銘柄が±10%を超えました。\n\n"
        body += "\n".join(alerts)
        body += f"\n\n{'='*30}\n全銘柄結果:\n"
        body += "\n".join(results)
        send_email(subject, body)
    else:
        print("全銘柄±10%以内（異常なし）")
 
    if errors:
        print(f"\n取得失敗: {len(errors)}件")
 
    print(f"{'='*50}\n")
 
if __name__ == "__main__":
    main()
