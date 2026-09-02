#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path("/root/MAJD-GIT")
STATE = ROOT / ".majd/platform-state.json"
SCHEDULER = ROOT / ".majd/scheduler.json"

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def service_state():
    try:
        return subprocess.check_output(
            ["systemctl", "is-active", "majd-git-autonomous.service"],
            text=True, timeout=3
        ).strip()
    except Exception:
        return "unknown"

def git_repositories():
    result = {}
    managed = ROOT / "managed"
    if not managed.exists():
        return result
    for repo in sorted(managed.iterdir()):
        if not repo.is_dir() or not (repo / ".git").exists():
            continue
        try:
            branch = subprocess.check_output(
                ["git", "-C", str(repo), "branch", "--show-current"],
                text=True, timeout=3
            ).strip() or "DETACHED"
            head = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                text=True, timeout=3
            ).strip()
            message = subprocess.check_output(
                ["git", "-C", str(repo), "log", "-1", "--pretty=%s"],
                text=True, timeout=3
            ).strip()
            dirty = bool(subprocess.check_output(
                ["git", "-C", str(repo), "status", "--porcelain"],
                text=True, timeout=3
            ).strip())
            result[repo.name] = {
                "branch": branch,
                "head": head,
                "last_commit": message,
                "dirty": dirty
            }
        except Exception as e:
            result[repo.name] = {"error": type(e).__name__}
    return result

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            state = load_json(STATE)
            scheduler = load_json(SCHEDULER)
            body = json.dumps({
                "system": "MAJD-GIT",
                "service": service_state(),
                "public_release": "BLOCKED_UNTIL_OWNER_RELEASE",
                "last_repository": scheduler.get("last_repository"),
                "repositories": state,
                "git": git_repositories()
            }, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        # Browser/UI routes fall back to the MAJD-GIT dashboard.
        # API routes remain explicit.
        html = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAJD-GIT</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#090d16;color:#eef3ff;font-family:Arial,sans-serif}
header{padding:28px;max-width:1200px;margin:auto}
h1{font-size:34px;margin:0 0 8px}.sub{color:#91a0ba}
main{max-width:1200px;margin:auto;padding:0 28px 40px}
.top{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-bottom:20px}
.card{background:#111827;border:1px solid #253047;border-radius:18px;padding:18px}
.label{font-size:13px;color:#91a0ba}.value{font-size:20px;font-weight:bold;margin-top:7px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.repo{background:#111827;border:1px solid #253047;border-radius:18px;padding:18px}
.repo h3{margin:0 0 12px}.state{font-weight:bold}.active{color:#5ee6a8}.wait{color:#ffca67}
small{color:#91a0ba;display:block;margin-top:8px;word-break:break-word}
footer{text-align:center;color:#66738c;padding:20px}
</style>
</head>
<body>
<header><h1>MAJD-GIT</h1><div class="sub">لوحة إدارة المنصات والذكاء الاصطناعي</div></header>
<main>
<div class="top">
<div class="card"><div class="label">النظام</div><div class="value">MAJD-GIT</div></div>
<div class="card"><div class="label">الخدمة التلقائية</div><div id="service" class="value">...</div></div>
<div class="card"><div class="label">المنصة الحالية</div><div id="current" class="value">...</div></div>
<div class="card"><div class="label">الإطلاق العام</div><div class="value wait">بأمر المالك فقط</div></div>
</div>
<div id="repos" class="grid"></div>
</main>
<footer>OWNER ROOT • MAJD-GIT</footer>
<script>
async function refresh(){
 try{
  const r=await fetch('/api/status',{cache:'no-store'});
  const d=await r.json();
  const s=document.getElementById('service');
  s.textContent=d.service;
  s.className='value '+(d.service==='active'?'active':'wait');
  document.getElementById('current').textContent=d.last_repository||'—';
  const repos=document.getElementById('repos');
  repos.innerHTML='';
  Object.entries(d.repositories||{}).forEach(([name,x])=>{
   const el=document.createElement('div');
   el.className='repo';
   const g=(d.git||{})[name]||{};
   el.innerHTML='<h3>'+name+'</h3>'+
     '<div class="label">الحالة</div><div class="state">'+(x.state||'WAITING')+'</div>'+
     '<small>الفرع: <span dir="ltr">'+(g.branch||'—')+'</span></small>'+
     '<small>آخر Commit: <span dir="ltr">'+(g.head||'—')+'</span></small>'+
     '<small>Git: '+(g.dirty ? 'تغييرات غير محفوظة' : 'نظيف')+'</small>'+
     '<small>آخر تحديث: <span dir="ltr">'+(x.updated_at ? new Date(x.updated_at).toLocaleString('ar-SA') : '—')+'</span></small>';
   repos.appendChild(el);
  });
 }catch(e){}
}
refresh();setInterval(refresh,5000);
</script>
</body></html>"""
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8095), Handler).serve_forever()
