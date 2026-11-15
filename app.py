import os
import socket
from datetime import datetime
from string import Template

from flask import Flask

app = Flask(__name__)

COLORS = {"blue": "#1d4ed8", "green": "#15803d"}

PAGE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blue-Green Deployment</title>
<style>
  body { margin:0; font-family: system-ui, Arial, sans-serif; background:$bg; color:#fff; }
  .wrap { max-width:760px; margin:0 auto; padding:64px 20px; text-align:center; }
  h1 { font-size:42px; margin:0 0 10px; }
  .badge { display:inline-block; padding:8px 18px; border-radius:999px; background:rgba(255,255,255,.18); font-weight:700; letter-spacing:.1em; }
  p { opacity:.85; font-size:18px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-top:34px; }
  .card { background:rgba(0,0,0,.25); border-radius:14px; padding:18px; text-align:left; }
  .card small { opacity:.75; text-transform:uppercase; letter-spacing:.08em; font-size:12px; }
  .card div { font-family: ui-monospace, Consolas, monospace; font-size:18px; margin-top:6px; word-break:break-all; }
  footer { margin-top:40px; opacity:.75; font-size:14px; }
</style>
</head>
<body>
<div class="wrap">
  <span class="badge">$color_upper ENVIRONMENT</span>
  <h1>Blue-Green Deployment</h1>
  <p>This version is running in the $color environment on Kubernetes.</p>
  <div class="grid">
    <div class="card"><small>Version (build)</small><div>$version</div></div>
    <div class="card"><small>Pod name</small><div>$pod</div></div>
    <div class="card"><small>Server time</small><div>$time</div></div>
  </div>
  <footer>Arjun V and Kanikshaa K | Essentials in Cloud and DevOps | SRM Institute</footer>
</div>
</body>
</html>""")


@app.route("/")
def home():
    color = os.environ.get("APP_COLOR", "blue")
    return PAGE.substitute(
        bg=COLORS.get(color, "#334155"),
        color=color,
        color_upper=color.upper(),
        version=os.environ.get("APP_VERSION", "0"),
        pod=socket.gethostname(),
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
