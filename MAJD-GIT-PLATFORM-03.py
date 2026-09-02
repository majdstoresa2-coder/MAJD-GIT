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


def owner_jobs():
    result = {}
    jobs_dir = ROOT / ".majd" / "owner-jobs"

    if not jobs_dir.exists():
        return result

    names = set()

    for x in jobs_dir.glob("*.log"):
        names.add(x.stem)

    for x in jobs_dir.glob("*.json"):
        names.add(x.stem)

    for name in sorted(names):
        log_path = jobs_dir / f"{name}.log"
        meta_path = jobs_dir / f"{name}.json"

        pid = None
        started_at = None

        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                pid = int(meta["pid"]) if meta.get("pid") else None
                started_at = meta.get("started_at")
            except Exception:
                pass

        running = bool(pid and Path(f"/proc/{pid}").exists())

        try:
            raw = log_path.read_text(
                encoding="utf-8",
                errors="replace"
            ) if log_path.exists() else ""
            tail = raw[-1200:].strip()
        except Exception:
            tail = ""

        result[name] = {
            "status": "RUNNING" if running else "FINISHED",
            "pid": pid,
            "started_at": started_at,
            "result": tail
        }

    return result


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
    def do_POST(self):
        try:
            if self.headers.get("X-MAJD-Owner-Control") != "1":
                raise PermissionError("owner control header required")

            if "application/json" not in self.headers.get("Content-Type", ""):
                raise ValueError("application/json required")

            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 2048:
                raise ValueError("invalid request size")

            body = json.loads(self.rfile.read(length).decode("utf-8"))

            # التحكم بالخدمة
            if self.path == "/api/owner/service":
                action = str(body.get("action", "")).strip().lower()

                allowed = {
                    "start": ["systemctl", "start", "majd-git-autonomous.service"],
                    "stop": ["systemctl", "stop", "majd-git-autonomous.service"],
                    "restart": ["systemctl", "restart", "majd-git-autonomous.service"],
                }

                if action not in allowed:
                    raise ValueError("action denied")

                cp = subprocess.run(
                    allowed[action],
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                payload = {
                    "ok": cp.returncode == 0,
                    "action": action,
                    "service": service_state(),
                    "public_release": "BLOCKED_UNTIL_OWNER_RELEASE"
                }

            # التحكم بالمستودعات
            elif self.path == "/api/owner/repository":
                name = str(body.get("repository", "")).strip()
                action = str(body.get("action", "")).strip().lower()

                managed = (ROOT / "managed").resolve()
                repo = (managed / name).resolve()

                if repo.parent != managed:
                    raise ValueError("repository denied")

                if not repo.is_dir() or not (repo / ".git").exists():
                    raise ValueError("repository not found")

                if action == "verify":
                    branch = subprocess.check_output(
                        ["git", "-C", str(repo), "branch", "--show-current"],
                        text=True, timeout=5
                    ).strip() or "DETACHED"

                    head = subprocess.check_output(
                        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                        text=True, timeout=5
                    ).strip()

                    status = subprocess.check_output(
                        ["git", "-C", str(repo), "status", "--porcelain"],
                        text=True, timeout=5
                    ).strip()

                    payload = {
                        "ok": True,
                        "repository": name,
                        "action": "verify",
                        "branch": branch,
                        "head": head,
                        "dirty": bool(status),
                        "public_release": "BLOCKED_UNTIL_OWNER_RELEASE"
                    }

                elif action == "sync":
                    status = subprocess.check_output(
                        ["git", "-C", str(repo), "status", "--porcelain"],
                        text=True, timeout=5
                    ).strip()

                    if status:
                        raise ValueError("repository has local changes; sync denied")

                    fetch = subprocess.run(
                        ["git", "-C", str(repo), "fetch", "--prune", "origin"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if fetch.returncode != 0:
                        raise RuntimeError("git fetch failed")

                    pull = subprocess.run(
                        ["git", "-C", str(repo), "pull", "--ff-only"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if pull.returncode != 0:
                        raise RuntimeError("fast-forward sync failed")

                    head = subprocess.check_output(
                        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                        text=True, timeout=5
                    ).strip()

                    payload = {
                        "ok": True,
                        "repository": name,
                        "action": "sync",
                        "head": head,
                        "result": pull.stdout.strip()[-500:],
                        "public_release": "BLOCKED_UNTIL_OWNER_RELEASE"
                    }

                elif action == "develop":
                    objective = (
                        f"Work only on managed repository {name}. "
                        "Inspect its current state, perform one bounded necessary production-ready improvement, "
                        "verify the result, protect OWNER_ROOT and secrets, and do not release publicly."
                    )

                    log_dir = ROOT / ".majd" / "owner-jobs"
                    log_dir.mkdir(parents=True, exist_ok=True)
                    log_path = log_dir / f"{name}.log"

                    with open(log_path, "ab") as log:
                        proc = subprocess.Popen(
                            [
                                "/usr/bin/python3",
                                str(ROOT / "MAJD-AI-MASTERMIND-01.py"),
                                "evolve",
                                objective
                            ],
                            cwd=str(ROOT),
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            start_new_session=True
                        )

                    
                    meta_path = log_dir / f"{name}.json"
                    meta_path.write_text(
                        json.dumps({
                            "pid": proc.pid,
                            "repository": name,
                            "started_at": __import__("datetime").datetime.now(
                                __import__("datetime").timezone.utc
                            ).isoformat()
                        }, ensure_ascii=False),
                        encoding="utf-8"
                    )

                    payload = {
                        "ok": True,
                        "repository": name,
                        "action": "develop",
                        "status": "STARTED",
                        "pid": proc.pid,
                        "public_release": "BLOCKED_UNTIL_OWNER_RELEASE"
                    }

                else:
                    raise ValueError("repository action denied")

            else:
                self.send_error(404)
                return

            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200 if payload.get("ok") else 500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except Exception as exc:
            data = json.dumps({
                "ok": False,
                "error": str(exc),
                "public_release": "BLOCKED_UNTIL_OWNER_RELEASE"
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

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
                "git": git_repositories(),
                "jobs": owner_jobs()
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
<div class="card"><div class="label">عدد المنصات</div><div id="repoCount" class="value">...</div></div>
<div class="card"><div class="label">Git نظيف</div><div id="cleanCount" class="value">...</div></div>
<div class="card"><div class="label">AI مؤجل</div><div id="deferredCount" class="value">...</div></div>
</div>
<div id="ownerControls" class="card" style="margin:18px 0">
<h3>تحكم المالك</h3>
<p>التحكم بالخدمة التلقائية فقط — الإطلاق العام يبقى مقفولًا.</p>
<button onclick="ownerService('start')">تشغيل الأتمتة</button>
<button onclick="ownerService('restart')">إعادة التشغيل</button>
<button onclick="ownerService('stop')">إيقاف الأتمتة</button>
<div id="ownerResult" style="margin-top:12px"></div>
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
  const repoEntries=Object.entries(d.repositories||{});
  const gitEntries=Object.values(d.git||{});
  document.getElementById('repoCount').textContent=repoEntries.length;
  document.getElementById('cleanCount').textContent=gitEntries.filter(g=>!g.dirty&&!g.error).length;
  document.getElementById('deferredCount').textContent=repoEntries.filter(([_,x])=>x.state==='AI_DEFERRED').length;
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
     '<small>الرسالة: '+(g.last_commit||'—')+'</small>'+
     '<small>Git: '+(g.dirty ? 'تغييرات غير محفوظة' : 'نظيف')+'</small>'+
     '<div style="margin-top:10px">'+
     '<button onclick="ownerRepo(\''+name+'\',\'verify\')">تحقق Git</button> '+
     '<button onclick="ownerRepo(\''+name+'\',\'sync\')">مزامنة آمنة</button> '+
     '<button onclick="ownerRepo(\''+name+'\',\'develop\')">تشغيل دورة تطوير</button>'+
     '</div>'+
     '<small id="jobStatus-'+name+'" style="display:block;margin-top:8px"></small>'+
     '<small id="jobResult-'+name+'" style="display:block;margin-top:6px;white-space:pre-wrap"></small>'+
     '<small id="repoResult-'+name+'" style="display:block;margin-top:8px"></small>'+
     '<small>آخر تحديث: <span dir="ltr">'+(x.updated_at ? new Date(x.updated_at).toLocaleString('ar-SA') : '—')+'</span></small>';
   repos.appendChild(el);

   const job=(d.jobs||{})[name];
   if(job){
     const statusEl=document.getElementById('jobStatus-'+name);
     const resultEl=document.getElementById('jobResult-'+name);

     if(statusEl){
       statusEl.textContent =
         job.status==='RUNNING'
         ? 'دورة التطوير: تعمل الآن'
         : 'دورة التطوير: انتهت';
     }

     if(resultEl && job.result){
       let txt=job.result;
       if(txt.length>500) txt=txt.slice(-500);
       resultEl.textContent='آخر نتيجة: '+txt;
     }
   }
  });
 }catch(e){}
}
refresh();setInterval(refresh,5000);

async function ownerService(action){
  const out=document.getElementById('ownerResult');
  out.textContent='جارٍ التنفيذ...';

  try{
    const r=await fetch('/api/owner/service',{
      method:'POST',
      headers:{'Content-Type':'application/json','X-MAJD-Owner-Control':'1'},
      body:JSON.stringify({action})
    });

    const d=await r.json();

    if(!r.ok || !d.ok){
      out.textContent='فشل التنفيذ';
      return;
    }

    out.textContent='تم التنفيذ — الخدمة: '+d.service;
    setTimeout(load,800);
  }catch(e){
    out.textContent='تعذر تنفيذ الأمر';
  }
}


async function ownerRepo(name,action){
  const out=document.getElementById('repoResult-'+name);
  out.textContent='جارٍ التنفيذ...';

  try{
    const r=await fetch('/api/owner/repository',{
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-MAJD-Owner-Control':'1'
      },
      body:JSON.stringify({
        repository:name,
        action:action
      })
    });

    const d=await r.json();

    if(!r.ok || !d.ok){
      out.textContent='رفض التنفيذ: '+(d.error||'خطأ');
      return;
    }

    if(action==='verify'){
      out.textContent='تم التحقق — '+d.branch+' / '+d.head+
        (d.dirty ? ' / توجد تغييرات' : ' / Git نظيف');
    }else if(action==='sync'){
      out.textContent='تمت المزامنة — '+d.head;
    }else if(action==='develop'){
      out.textContent=d.ok ? 'بدأت دورة التطوير في الخلفية' : 'فشلت بداية دورة التطوير';
    }

    setTimeout(load,800);
  }catch(e){
    out.textContent='تعذر تنفيذ العملية';
  }
}

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
