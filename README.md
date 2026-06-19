# SUBNET_CALCULATOR

## Author

- Name: N.Kugan
- Project: SUBNET_CALCULATOR

Built with Flask (Python) — no external JS frameworks needed.

## Features
- Enter any IPv4 network address + prefix length
- View subnet address, netmask, IP range, usable IPs, and host count
- See wildcard mask, binary netmask, address type, and IP class
- View subnet position with a visual address-space diagram per row
- See network vs host bit boundaries with a 32-bit visual mask bar
- View VLAN segregation and switch-connectivity topology in the network diagram
- **Divide** any subnet into two equal halves (recursive splitting)
- **Join** two adjacent sibling subnets back into their parent
- Automatic visual updates after calculate, split, and join actions
- Light-themed UI with depth indicators and legends

## Prerequisites
- Python 3.9 or newer
- `pip` package manager

Check versions:

```bash
python --version
pip --version
```

## Installation

1. Open a terminal in the project folder.
2. (Optional but recommended) Create a virtual environment.
3. Install dependencies from `requirements.txt`.

```bash
# Optional virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Install required package(s)
pip install -r requirements.txt
```

## Run The App

1. Start Flask app:

```bash
python app.py
```

2. Open browser:

```text
http://localhost:5000
```

## Publish As A Web App

This project is ready to publish as a hosted website using a Python web platform such as Render, Railway, Fly.io, PythonAnywhere, or a VPS.

### Files Used For Deployment

- [wsgi.py](wsgi.py) exposes the Flask app for production servers.
- [Procfile](Procfile) tells hosts to launch the app with Gunicorn.
- [requirements.txt](requirements.txt) includes `gunicorn` for production serving.

### Publish Steps

1. Push the project to a Git repository such as GitHub.
2. Create a new web service on your hosting platform.
3. Set the start command to:

```bash
gunicorn wsgi:app
```

4. Set the app environment to Python.
5. Deploy the service.
6. Open the public URL provided by the host.

### Recommended Environment Variables

- `PORT` for the server port if your host requires it.
- `FLASK_DEBUG=1` only for local development.

### Optional WordPress Integration

If you want to show this app inside a WordPress site, deploy it separately and embed it with an iframe or link it from a WordPress page.

## Step-By-Step Usage

1. Enter a network address (example: `192.168.0.0`).
2. Choose mask bits (example: `/24`).
3. Click `CALCULATE`.
4. Review summary cards:
	 - Root CIDR
	 - Subnet count
	 - Total addresses
	 - Address type
	 - IP class
5. Inspect visual sections:
	 - Address-space map bars
	 - 32-bit network/host boundary diagram
	 - VLAN segregation and switch-connectivity topology
6. Click `÷ SPLIT` to divide a subnet.
7. Click `⊕ JOIN` to merge sibling subnets.
8. Watch all diagrams and counters auto-refresh after every action.

## Project Structure

```text
.
├── app.py            # Flask app, HTML/CSS/JS UI, subnet logic
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```

## How It Works

- **Backend**: Flask handles subnet calculations using Python `ipaddress`.
- **Frontend**: Vanilla JavaScript calls Flask endpoints via Fetch API.
- **Auto Refresh**: One render cycle updates table + summary + diagrams after each API response.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/calculate` | Initialize with a network and mask |
| POST | `/api/divide` | Split selected subnet into two children |
| POST | `/api/join` | Merge two sibling subnets into parent |

### API Request Examples

`/api/calculate`

```json
{
	"network": "192.168.0.0",
	"mask": "24"
}
```

`/api/divide`

```json
{
	"subnets": [
		{
			"network": "192.168.0.0",
			"prefix": 24,
			"base_prefix": 24
		}
	],
	"index": 0
}
```

`/api/join`

```json
{
	"subnets": [
		{
			"network": "192.168.0.0",
			"prefix": 25,
			"base_prefix": 24
		},
		{
			"network": "192.168.0.128",
			"prefix": 25,
			"base_prefix": 24
		}
	],
	"index": 1
}
```

## Troubleshooting

- If `flask` import fails:

```bash
pip install -r requirements.txt
```

- If port `5000` is in use, change port in `app.py`.
- If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```



