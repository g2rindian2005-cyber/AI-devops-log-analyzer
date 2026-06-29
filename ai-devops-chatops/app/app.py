"""
AI DevOps ChatOps Platform
Main Flask Application
"""

import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# ── Google Gemini (new SDK) ───────────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")
SLACK_WEBHOOK    = os.getenv("SLACK_WEBHOOK_URL", "")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
PROMETHEUS_URL   = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

# Initialise Gemini client
gemini_client = None
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini AI client initialised")
    except Exception as e:
        logger.warning(f"Gemini init failed: {e}")
else:
    logger.warning("GEMINI_API_KEY not set — AI features disabled")

# ─── HTML Dashboard ───────────────────────────────────────────────────────────
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI DevOps ChatOps Platform</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh}
    header{background:linear-gradient(135deg,#161b22,#21262d);border-bottom:1px solid #30363d;
      padding:20px 40px;display:flex;align-items:center;gap:16px}
    header h1{color:#58a6ff;font-size:1.6rem}
    header span{background:#238636;color:#fff;font-size:.75rem;padding:3px 10px;border-radius:20px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;padding:30px 40px}
    .card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:24px}
    .card h3{color:#58a6ff;margin-bottom:12px;font-size:1rem}
    .badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.8rem;font-weight:600;margin:4px 2px}
    .green{background:#1a3a1a;color:#3fb950;border:1px solid #2ea043}
    .blue{background:#0d2a4a;color:#58a6ff;border:1px solid #388bfd}
    .yellow{background:#3a2a0a;color:#d29922;border:1px solid #9e6a03}
    .chat-box{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;
      height:200px;overflow-y:auto;margin-bottom:12px;font-family:monospace;font-size:.85rem}
    .chat-input{display:flex;gap:8px}
    .chat-input input{flex:1;background:#21262d;border:1px solid #30363d;color:#c9d1d9;
      padding:10px 14px;border-radius:8px;outline:none}
    .chat-input button{background:#238636;color:#fff;border:none;padding:10px 20px;
      border-radius:8px;cursor:pointer}
    .chat-input button:hover{background:#2ea043}
    .msg{margin:6px 0}
    .msg.user{color:#58a6ff}
    .msg.bot{color:#3fb950}
    .endpoints{padding:0 40px 30px}
    .endpoints table{width:100%;border-collapse:collapse;background:#161b22;border-radius:12px;overflow:hidden}
    .endpoints th{background:#21262d;padding:12px 16px;text-align:left;color:#8b949e;
      font-size:.85rem;border-bottom:1px solid #30363d}
    .endpoints td{padding:12px 16px;border-bottom:1px solid #21262d;font-family:monospace;font-size:.85rem}
  </style>
</head>
<body>
  <header>
    <h1>🤖 AI DevOps ChatOps Platform</h1>
    <span>LIVE</span>
  </header>

  <div class="grid">
    <div class="card">
      <h3>📊 Platform Status</h3>
      <p style="margin-bottom:10px;font-size:.85rem;color:#8b949e">All systems operational</p>
      <span class="badge green">✓ API Online</span>
      <span class="badge green">✓ AI Ready</span>
      <span class="badge blue">✓ Monitoring</span>
      <span class="badge yellow">⚡ Notifications</span>
    </div>

    <div class="card">
      <h3>🛠 Tech Stack</h3>
      <span class="badge blue">AWS EC2</span>
      <span class="badge blue">Docker</span>
      <span class="badge blue">Kubernetes</span>
      <span class="badge green">Terraform</span>
      <span class="badge green">GitHub Actions</span>
      <span class="badge yellow">Prometheus</span>
      <span class="badge yellow">Grafana</span>
      <span class="badge blue">Gemini AI</span>
    </div>

    <div class="card" style="grid-column:span 2">
      <h3>💬 AI DevOps Assistant</h3>
      <div class="chat-box" id="chatBox">
        <div class="msg bot">🤖 Hello! Ask me about Kubernetes errors, log analysis, or DevOps best practices.</div>
      </div>
      <div class="chat-input">
        <input type="text" id="userInput" placeholder="e.g. Explain CrashLoopBackOff…"/>
        <button onclick="sendMessage()">Send</button>
      </div>
    </div>
  </div>

  <div class="endpoints">
    <h3 style="color:#58a6ff;margin-bottom:14px">📡 API Endpoints</h3>
    <table>
      <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>GET</td><td>/health</td><td>Health check</td></tr>
        <tr><td>POST</td><td>/ai/chat</td><td>AI DevOps chatbot</td></tr>
        <tr><td>POST</td><td>/ai/explain-error</td><td>Explain K8s / Docker errors</td></tr>
        <tr><td>POST</td><td>/ai/analyse-logs</td><td>AI log analysis</td></tr>
        <tr><td>GET</td><td>/metrics/summary</td><td>Prometheus metrics summary</td></tr>
        <tr><td>POST</td><td>/notify/slack</td><td>Send Slack notification</td></tr>
        <tr><td>POST</td><td>/notify/telegram</td><td>Send Telegram notification</td></tr>
        <tr><td>POST</td><td>/webhook/deployment</td><td>GitHub Actions deployment hook</td></tr>
      </tbody>
    </table>
  </div>

  <script>
    async function sendMessage() {
      const input = document.getElementById('userInput');
      const box   = document.getElementById('chatBox');
      const text  = input.value.trim();
      if (!text) return;
      box.innerHTML += `<div class="msg user">👤 ${text}</div>`;
      input.value = '';
      box.scrollTop = box.scrollHeight;
      try {
        const res  = await fetch('/ai/chat', {method:'POST',
          headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
        const data = await res.json();
        box.innerHTML += `<div class="msg bot">🤖 ${data.response || data.error}</div>`;
      } catch(e) {
        box.innerHTML += `<div class="msg bot" style="color:#f85149">❌ ${e.message}</div>`;
      }
      box.scrollTop = box.scrollHeight;
    }
    document.getElementById('userInput').addEventListener('keypress',
      e => { if (e.key==='Enter') sendMessage(); });
  </script>
</body>
</html>
"""

# ─── Helper: call Gemini ──────────────────────────────────────────────────────
def ask_gemini(prompt: str) -> str:
    if not gemini_client:
        return "AI not configured. Please set GEMINI_API_KEY."
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"AI error: {str(e)}"

# ─── Helper: send Slack ───────────────────────────────────────────────────────
def send_slack(message: str) -> bool:
    if not SLACK_WEBHOOK:
        return False
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
        return True
    except Exception as e:
        logger.error(f"Slack error: {e}")
        return False

# ─── Helper: send Telegram ────────────────────────────────────────────────────
def send_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
        return True
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_enabled": gemini_client is not None,
        "slack_enabled": bool(SLACK_WEBHOOK),
        "telegram_enabled": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "version": "1.0.0"
    })

@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "No message provided"}), 400
    prompt = (
        "You are an expert DevOps AI assistant. "
        "Help with Kubernetes, Docker, Terraform, CI/CD, AWS, and monitoring tools. "
        f"Be concise and practical.\n\nUser: {message}"
    )
    response = ask_gemini(prompt)
    logger.info(f"Chat — user: {message[:60]}…")
    return jsonify({"response": response, "timestamp": datetime.utcnow().isoformat()})

@app.route("/ai/explain-error", methods=["POST"])
def explain_error():
    data = request.get_json(silent=True) or {}
    error = data.get("error", "").strip()
    context = data.get("context", "Kubernetes/Docker")
    if not error:
        return jsonify({"error": "No error message provided"}), 400
    prompt = (
        f"You are a DevOps expert. Analyse this {context} error and provide:\n"
        f"1. Root cause\n2. Step-by-step fix\n3. Prevention tip\n\nError:\n{error}"
    )
    explanation = ask_gemini(prompt)
    notif = f"🚨 DevOps Error: {error[:200]}\n💡 AI Analysis ready."
    send_slack(notif)
    send_telegram(notif)
    return jsonify({
        "error_input": error,
        "explanation": explanation,
        "notifications_sent": {"slack": bool(SLACK_WEBHOOK), "telegram": bool(TELEGRAM_TOKEN)},
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/ai/analyse-logs", methods=["POST"])
def analyse_logs():
    data = request.get_json(silent=True) or {}
    logs = data.get("logs", "").strip()
    if not logs:
        return jsonify({"error": "No logs provided"}), 400
    prompt = (
        "You are a DevOps log analysis expert. Analyse these logs and provide:\n"
        "1. Summary of what happened\n2. Any errors or warnings\n3. Recommended actions\n\n"
        f"Logs:\n{logs[:3000]}"
    )
    analysis = ask_gemini(prompt)
    return jsonify({
        "analysis": analysis,
        "log_lines": len(logs.splitlines()),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/metrics/summary", methods=["GET"])
def metrics_summary():
    metrics = {}
    queries = {
        "cpu_usage":    'avg(rate(container_cpu_usage_seconds_total[5m])) * 100',
        "memory_usage": 'avg(container_memory_usage_bytes) / 1024 / 1024',
        "http_requests":'sum(rate(http_requests_total[5m]))',
    }
    for name, query in queries.items():
        try:
            r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
                             params={"query": query}, timeout=3)
            result = r.json().get("data", {}).get("result", [])
            metrics[name] = float(result[0]["value"][1]) if result else None
        except Exception:
            metrics[name] = None
    return jsonify({"metrics": metrics, "prometheus_url": PROMETHEUS_URL,
                    "timestamp": datetime.utcnow().isoformat()})

@app.route("/notify/slack", methods=["POST"])
def notify_slack():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "No message provided"}), 400
    return jsonify({"sent": send_slack(message), "channel": "Slack"})

@app.route("/notify/telegram", methods=["POST"])
def notify_telegram():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "No message provided"}), 400
    return jsonify({"sent": send_telegram(message), "channel": "Telegram"})

@app.route("/webhook/deployment", methods=["POST"])
def deployment_webhook():
    data = request.get_json(silent=True) or {}
    repo   = data.get("repository", "unknown")
    status = data.get("status", "unknown")
    branch = data.get("branch", "main")
    env    = data.get("environment", "production")
    msg = f"🚀 Deployment {status.upper()} | {repo} | Branch: {branch} | Env: {env}"
    send_slack(msg)
    send_telegram(msg)
    if status == "failed":
        error_info = data.get("error", "Deployment failed")
        ai_advice = ask_gemini(
            f"Deployment to {env} failed for {repo} on {branch}.\nError: {error_info}\n"
            "Provide a concise troubleshooting guide."
        )
        send_slack(f"🤖 AI Advice:\n{ai_advice[:500]}")
    return jsonify({"received": True, "notifications_sent": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
