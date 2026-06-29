# 🤖 AI DevOps ChatOps Platform

An AI-powered DevOps platform that combines Kubernetes, Docker, Terraform, GitHub Actions, Prometheus, Grafana, and Google Gemini AI into one deployable project.

---

## 🏗 Project Structure

```
ai-devops-chatops/
├── app/
│   ├── app.py              # Flask application (AI + APIs)
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container build
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # GitHub Actions CI/CD pipeline
├── k8s/
│   └── deployment.yaml     # Kubernetes manifests (Deployment, Service, HPA)
├── terraform/
│   ├── main.tf             # AWS EKS + VPC infrastructure
│   └── variables.tf        # Terraform variables
├── monitoring/
│   ├── prometheus.yml      # Prometheus scrape config
│   └── grafana-datasource.yml
├── docker-compose.yml      # Local dev (App + Prometheus + Grafana)
├── .env.example            # Environment variables template
└── README.md
```

---

## ⚡ Quick Start — Run Locally (Docker Compose)

### Step 1 — Prerequisites
```bash
# Install Docker Desktop (includes Docker Compose)
# https://www.docker.com/products/docker-desktop/
docker --version      # should show 24+
docker compose version
```

### Step 2 — Clone & Configure
```bash
git clone https://github.com/YOUR_USERNAME/ai-devops-chatops.git
cd ai-devops-chatops

# Copy and edit environment variables
cp .env.example .env
nano .env   # fill in GEMINI_API_KEY at minimum
```

### Step 3 — Start Everything
```bash
docker compose up --build -d
```

### Step 4 — Open in Browser
| Service | URL | Credentials |
|---|---|---|
| **App Dashboard** | http://localhost:5000 | — |
| **Prometheus** | http://localhost:9090 | — |
| **Grafana** | http://localhost:3000 | admin / admin123 |

### Step 5 — Stop
```bash
docker compose down
```

---

## 🧪 Test the API

```bash
# Health check
curl http://localhost:5000/health

# AI Chat
curl -X POST http://localhost:5000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I debug a CrashLoopBackOff in Kubernetes?"}'

# Explain a K8s error
curl -X POST http://localhost:5000/ai/explain-error \
  -H "Content-Type: application/json" \
  -d '{"error": "OOMKilled", "context": "Kubernetes"}'

# Analyse logs
curl -X POST http://localhost:5000/ai/analyse-logs \
  -H "Content-Type: application/json" \
  -d '{"logs": "ERROR: connection refused\nWARN: retry attempt 3\nERROR: timeout"}'
```

---

## ☁️ Deploy to AWS EKS

### Prerequisites
- AWS account with IAM permissions for EKS, EC2, VPC
- AWS CLI configured (`aws configure`)
- Terraform >= 1.5 installed
- kubectl installed

### Step 1 — Provision Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

### Step 2 — Configure kubectl
```bash
aws eks update-kubeconfig --name ai-devops-chatops-eks --region ap-south-1
kubectl get nodes   # should show 2 nodes
```

### Step 3 — Push Docker Image
```bash
docker build -t YOUR_DOCKERHUB_USERNAME/ai-devops-chatops:latest ./app
docker push YOUR_DOCKERHUB_USERNAME/ai-devops-chatops:latest
```

### Step 4 — Create Kubernetes Secrets
```bash
kubectl create namespace chatops

kubectl create secret generic chatops-secrets \
  --from-literal=GEMINI_API_KEY=your_key \
  --from-literal=SLACK_WEBHOOK_URL=your_webhook \
  --from-literal=TELEGRAM_BOT_TOKEN=your_token \
  --from-literal=TELEGRAM_CHAT_ID=your_chat_id \
  -n chatops
```

### Step 5 — Deploy to Kubernetes
```bash
# Edit k8s/deployment.yaml — replace YOUR_DOCKERHUB_USERNAME
kubectl apply -f k8s/deployment.yaml
kubectl get pods -n chatops
kubectl get svc chatops-service -n chatops   # get external URL
```

---

## 🔄 GitHub Actions CI/CD

Add these secrets to your GitHub repo (Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `AWS_ACCESS_KEY_ID` | AWS IAM key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret |
| `AWS_REGION` | e.g. `ap-south-1` |
| `EKS_CLUSTER_NAME` | `ai-devops-chatops-eks` |
| `SLACK_WEBHOOK_URL` | Slack webhook (optional) |

Every push to `main` → builds image → pushes to Docker Hub → deploys to EKS.

---

## 🔑 Getting API Keys

### Gemini API Key (Free)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into `.env`

### Slack Webhook (Free)
1. https://api.slack.com/messaging/webhooks
2. Create App → Incoming Webhooks → Activate → Add to Workspace

### Telegram Bot (Free)
1. Open Telegram → search `@BotFather`
2. `/newbot` → follow steps → copy token
3. Get chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

## 📊 Monitoring

- **Prometheus** collects metrics at `http://localhost:9090`
- **Grafana** visualises at `http://localhost:3000` (Prometheus datasource pre-configured)
- Add dashboards: Import ID `1860` (Node Exporter Full) or `6417` (Kubernetes)

---

## 🛠 Skills Demonstrated

| Skill | Tool |
|---|---|
| Cloud Infrastructure | AWS EC2, EKS, VPC via Terraform |
| Containerisation | Docker, multi-stage builds |
| Orchestration | Kubernetes Deployments, Services, HPA |
| CI/CD | GitHub Actions (build → test → push → deploy) |
| AI Integration | Google Gemini API |
| Monitoring | Prometheus + Grafana |
| Notifications | Slack + Telegram webhooks |
| IaC | Terraform modules |

---

## 👤 Author
**Gokul Ram Rathod** — Aspiring DevOps Engineer  
GitHub: github.com/g2rindian2005-cyber  
LinkedIn: linkedin.com/in/gokul-rathod-3325072b9
