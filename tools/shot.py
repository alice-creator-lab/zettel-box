#!/usr/bin/env python3
"""卡片盒 — 手機尺寸自動測試與截圖。用法：python3 tools/shot.py [url]"""
import json, os, random, subprocess, sys, time, urllib.request

CHROME = os.path.expanduser("~/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome")
PORT = random.randint(9400, 9500)
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8811/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shots")
sys.path.insert(0, os.path.expanduser("~/.hermes/profiles/friend/cache/scratch"))
from cdp import Page  # noqa: E402


def launch(w, h):
    args = [CHROME, "--headless=new", f"--remote-debugging-port={PORT}", f"--window-size={w},{h}",
            "--no-first-run", "--hide-scrollbars", f"--user-data-dir=/tmp/zb-{PORT}",
            "--force-device-scale-factor=2", "about:blank"]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
            return p
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("chrome failed")


def main():
    os.makedirs(OUT, exist_ok=True)
    w, h = 390, 844
    proc = launch(w, h)
    page = Page(PORT, match="about:blank")
    errs = []
    try:
        page.send("Emulation.setDeviceMetricsOverride",
                  {"width": w, "height": h, "deviceScaleFactor": 2, "mobile": True})
        page.nav(URL, timeout=60)
        page.js("window.__errs=[];addEventListener('error',e=>__errs.push(e.message));"
                "addEventListener('unhandledrejection',e=>__errs.push('rej:'+(e.reason&&e.reason.message||e.reason)))")
        for _ in range(50):
            if page.js("!!window.__app"):
                break
            time.sleep(0.2)
        print("boot:", page.js("!!window.__app"), "| version", page.js("window.__app&&__app.VERSION"))

        # 1) 收件匣：寫兩則
        for txt in ["Heptabase 的白板令空間變成記憶的一部分",
                    "每張卡只講一個想法，連結時要寫理由"]:
            page.js(f"(()=>{{const t=document.querySelector('#capText');t.value={json.dumps(txt)};"
                    "t.dispatchEvent(new Event('input',{bubbles:true}));"
                    "document.querySelector('[data-act=capture]').click();})()")
            time.sleep(0.35)
        print("inbox rows:", page.js("document.querySelectorAll('#inboxList .row').length"),
              "| cards:", page.js("__app.S.cards.length"))
        page.shot(os.path.join(OUT, "1-inbox.png"))

        # 2) 升級第一則 → 永久筆記
        page.js("document.querySelector('#inboxList [data-act=upgrade]').click()")
        time.sleep(0.4)
        page.shot(os.path.join(OUT, "2-upgrade-sheet.png"))
        page.js("document.querySelector('#sheetBody [data-sheet-i=\"0\"]').click()")
        time.sleep(0.5)
        print("detail open:", page.js("document.querySelector('#detail').classList.contains('on')"),
              "| type:", page.js("(document.querySelector('#dTypes button.on')||{}).textContent"))

        # 3) 編輯詳情 + wiki 連結
        page.js("(()=>{const t=document.querySelector('#dTitle');t.value='白板就是記憶宮殿';"
                "t.dispatchEvent(new Event('input',{bubbles:true}));"
                "const b=document.querySelector('#dBody');"
                "b.value='Heptabase 把卡片放在二維空間，位置本身成為線索。\\n\\n- 相近的想法放近\\n- 用箭頭表示因果\\n\\n參見 [[白板就是記憶宮殿2]]';"
                "b.dispatchEvent(new Event('input',{bubbles:true}));})()")
        time.sleep(0.8)
        page.shot(os.path.join(OUT, "3-detail.png"))
        print("saved title:", page.js("__app.S.cards.find(c=>c.type!=='fleeting')?.title"))
        page.js("document.querySelector('[data-act=d-prev]').click()")
        time.sleep(0.4)
        page.shot(os.path.join(OUT, "4-preview.png"))
        page.js("document.querySelector('[data-act=close-detail]').click()")
        time.sleep(0.6)

        # 4) 卡片庫
        page.js("document.querySelector('.tab[data-view=cards]').click()")
        time.sleep(0.4)
        print("library rows:", page.js("document.querySelectorAll('#libList .row').length"))
        page.shot(os.path.join(OUT, "5-library.png"))

        # 5) 白板：加入兩張卡
        page.js("document.querySelector('.tab[data-view=board]').click()")
        time.sleep(0.5)
        for pick in (0, 0):
            page.js("document.querySelector('[data-act=board-add]').click()")
            time.sleep(0.35)
            page.js("document.querySelector('#sheetBody [data-sheet-i=\"1\"]').click()")
            time.sleep(0.4)
            page.js(f"document.querySelectorAll('#pickList [data-pick]')[{pick}].click()")
            time.sleep(0.5)
        print("nodes:", page.js("document.querySelectorAll('.node').length"),
              "| pos:", page.js("__app.S.pos.length"))
        page.shot(os.path.join(OUT, "6-board.png"))

        # 6) 拖動節點
        box = page.js("(()=>{const n=document.querySelector('.node');const r=n.getBoundingClientRect();"
                      "return {x:r.x+r.width/2,y:r.y+20,left:n.style.left,top:n.style.top}})()")
        if box:
            for typ in ("mousePressed", "mouseMoved", "mouseReleased"):
                page.send("Input.dispatchMouseEvent",
                          {"type": typ, "x": box["x"] + (60 if typ != "mousePressed" else 0),
                           "y": box["y"] + (40 if typ != "mousePressed" else 0),
                           "button": "left", "clickCount": 1})
        time.sleep(0.4)
        print("node moved:", box["left"], "->", page.js("document.querySelector('.node').style.left"))

        # 7) 連結模式：點兩張卡 → 寫理由
        page.js("document.querySelector('[data-act=link-mode]').click()")
        time.sleep(0.3)
        tap = ("(()=>{const n=document.querySelectorAll('.node')[IDX];const r=n.getBoundingClientRect();"
               "const o={clientX:r.x+40,clientY:r.y+30,pointerId:1,bubbles:true,isPrimary:true};"
               "n.dispatchEvent(new PointerEvent('pointerdown',o));"
               "n.dispatchEvent(new PointerEvent('pointerup',o));})()")
        page.js(tap.replace("IDX", "0"))
        time.sleep(0.3)
        page.js(tap.replace("IDX", "1"))
        time.sleep(0.5)
        print("reason sheet:", page.js("!!document.querySelector('#whyInput')"))
        page.js("(()=>{const w=document.querySelector('#whyInput');w.value='兩者都在講空間記憶';"
                "document.querySelector('#whySave').click();})()")
        time.sleep(0.6)
        print("links:", page.js("__app.S.links.length"), "| edges:", page.js("document.querySelectorAll('.edge').length"))
        page.shot(os.path.join(OUT, "7-board-links.png"))

        # 7) 重新載入，確認資料仍在
        page.nav(URL, timeout=60)
        for _ in range(40):
            if page.js("!!window.__app"):
                break
            time.sleep(0.2)
        print("after reload cards:", page.js("__app.S.cards.length"),
              "| links:", page.js("__app.S.links.length"),
              "| pos:", page.js("__app.S.pos.length"))

        page.js("document.querySelector('.tab[data-view=more]').click()")
        time.sleep(0.3)
        page.shot(os.path.join(OUT, "8-more.png"))

        # 8) 匯入備份（覆寫 confirm）
        page.js("window.confirm=()=>true")
        page.js("(async()=>{const n=new Date().toISOString();"
                "const data={cards:[{id:'c_t1',type:'permanent',title:'匯入測試卡',body:'內容來自備份檔',tags:['測試'],source:'',created:n,updated:n}],"
                "links:[],boards:[{id:'b_t1',name:'思考白板',created:n}],pos:[]};"
                "const f=new File([JSON.stringify(data)],'t.json',{type:'application/json'});"
                "await importJSON(f);})()")
        time.sleep(0.8)
        print("after import:", page.js("__app.S.cards.length"), page.js("__app.S.cards[0] && __app.S.cards[0].title"))

        # 9) 深色模式
        page.js("document.querySelector('.tab[data-view=cards]').click()")
        time.sleep(0.3)
        page.js("document.querySelectorAll('#themeSeg button')[1].click()")
        time.sleep(0.5)
        page.shot(os.path.join(OUT, "9-dark.png"))
        page.js("document.querySelectorAll('#themeSeg button')[0].click()")

        # 10) 長按節點選單
        page.js("document.querySelector('.tab[data-view=board]').click()")
        time.sleep(0.5)
        page.js("(async()=>{await placeCard('c_t1');renderBoard();})()")
        time.sleep(0.6)
        page.js("(()=>{const n=document.querySelector('.node');if(!n)return;const r=n.getBoundingClientRect();"
                "const o={clientX:r.x+30,clientY:r.y+24,pointerId:7,bubbles:true,isPrimary:true};"
                "n.dispatchEvent(new PointerEvent('pointerdown',o));})()")
        time.sleep(0.7)
        print("long-press menu:", page.js("document.querySelector('#sheet').classList.contains('on')"),
              "|", page.js("document.querySelector('#sheetTitle').textContent"))
        page.shot(os.path.join(OUT, "10-node-menu.png"))

        print("JS errors:", page.js("JSON.stringify(window.__errs||[])"))
    finally:
        page.close()
        proc.terminate()


if __name__ == "__main__":
    main()
