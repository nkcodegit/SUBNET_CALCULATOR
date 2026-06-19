from flask import Flask, render_template_string, request, jsonify
import ipaddress
import json
import os

app = Flask(__name__)


def ipv4_class(ipv4_addr):
  first = int(str(ipv4_addr).split('.')[0])
  if 1 <= first <= 126:
    return "A"
  if 128 <= first <= 191:
    return "B"
  if 192 <= first <= 223:
    return "C"
  if 224 <= first <= 239:
    return "D (Multicast)"
  return "E (Reserved)"


def mask_to_binary(mask):
  return '.'.join(f"{int(octet):08b}" for octet in str(mask).split('.'))

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title># SUBNET_CALCULATOR</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

  :root {
    --bg: #f5f8fc;
    --panel: #ffffff;
    --border: #d6deea;
    --accent: #0066d6;
    --accent2: #d66a00;
    --green: #0f9d58;
    --text: #1c2b40;
    --muted: #5f738f;
    --row-even: #f8fbff;
    --row-odd: #f1f6fd;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse at 20% 20%, rgba(0,102,214,0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(214,106,0,0.07) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }

  .scanlines {
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.025) 2px,
      rgba(0,0,0,0.025) 4px
    );
    pointer-events: none;
    z-index: 1;
  }

  .container {
    position: relative;
    z-index: 2;
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
  }

  header {
    margin-bottom: 40px;
    display: flex;
    align-items: baseline;
    gap: 16px;
  }

  h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 28px;
    color: var(--accent);
    text-shadow: 0 0 20px rgba(0,102,214,0.25);
    letter-spacing: 2px;
  }

  .subtitle {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  .input-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    padding: 28px 32px;
    margin-bottom: 32px;
    display: flex;
    align-items: flex-end;
    gap: 24px;
    flex-wrap: wrap;
    box-shadow: 0 8px 28px rgba(19, 45, 83, 0.08), inset 0 1px 0 rgba(0,102,214,0.08);
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  label {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
  }

  input[type="text"], select {
    background: #f9fbff;
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 16px;
    padding: 10px 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    -webkit-appearance: none;
  }

  input[type="text"] { width: 200px; }
  select { width: 100px; cursor: pointer; }

  input[type="text"]:focus, select:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0,102,214,0.12);
  }

  .slash {
    font-family: 'Share Tech Mono', monospace;
    font-size: 24px;
    color: var(--muted);
    padding-bottom: 10px;
  }

  button {
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 11px 28px;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    box-shadow: 0 8px 20px rgba(0,102,214,0.28);
  }

  .btn-primary:hover {
    background: #0f73e2;
    box-shadow: 0 10px 26px rgba(0,102,214,0.34);
    transform: translateY(-1px);
  }

  .btn-divide {
    background: transparent;
    border: 1px solid var(--accent2);
    color: var(--accent2);
    font-size: 11px;
    padding: 5px 12px;
    letter-spacing: 1px;
  }

  .btn-divide:hover {
    background: var(--accent2);
    color: #fff;
    box-shadow: 0 8px 18px rgba(214,106,0,0.25);
  }

  .btn-join {
    background: transparent;
    border: 1px solid var(--muted);
    color: var(--muted);
    font-size: 11px;
    padding: 5px 12px;
    letter-spacing: 1px;
  }

  .btn-join:hover:not(:disabled) {
    border-color: var(--green);
    color: var(--green);
    box-shadow: 0 8px 18px rgba(15,157,88,0.18);
  }

  .btn-join:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .table-wrap {
    background: var(--panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--muted);
    overflow: hidden;
    box-shadow: 0 8px 28px rgba(19, 45, 83, 0.08);
  }

  .summary-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    padding: 18px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: repeat(5, minmax(130px, 1fr));
    gap: 10px;
  }

  .summary-card {
    background: linear-gradient(160deg, #fbfdff 0%, #f3f8ff 100%);
    border: 1px solid var(--border);
    padding: 12px;
    border-radius: 6px;
  }

  .summary-label {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .summary-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    color: var(--text);
  }

  .legend-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 12px 14px;
    margin-bottom: 18px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 14px;
  }

  .legend-title {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-right: 2px;
  }

  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text);
    font-size: 11px;
    letter-spacing: 1px;
  }

  .legend-chip {
    width: 16px;
    height: 8px;
    border-radius: 4px;
    border: 1px solid rgba(28, 43, 64, 0.2);
  }

  .legend-chip.address {
    background: linear-gradient(90deg, rgba(0, 102, 214, 0.75) 0%, rgba(15, 157, 88, 0.75) 100%);
  }

  .legend-chip.network {
    background: #2a7fe0;
  }

  .legend-chip.host {
    background: #86b6eb;
  }

  .legend-chip.vlan {
    background: linear-gradient(90deg, #1f7ae0 0%, #35a66a 100%);
  }

  .diagram-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    padding: 14px;
    margin-bottom: 18px;
  }

  .diagram-title {
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .diagram-track {
    position: relative;
    height: 56px;
    border-radius: 10px;
    overflow: hidden;
    background: #edf3fb;
    border: 1px solid #d8e3f1;
  }

  .diagram-block {
    position: absolute;
    top: 0;
    height: 100%;
    border-right: 1px solid rgba(255, 255, 255, 0.75);
    padding: 5px 6px;
    color: #ffffff;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
    overflow: hidden;
    white-space: nowrap;
  }

  .diagram-block-label {
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1.2;
  }

  .diagram-block-meta {
    font-size: 10px;
    opacity: 0.95;
  }

  .diagram-switch-wrap {
    margin-top: 14px;
    border-top: 1px dashed #d5e1f1;
    padding-top: 12px;
  }

  .diagram-switch-title {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .switch-svg {
    width: 100%;
    height: auto;
    max-height: 260px;
    background: #f7faff;
    border: 1px solid #dce7f5;
    border-radius: 10px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
  }

  thead th {
    background: #f5f9ff;
    padding: 14px 16px;
    text-align: left;
    font-family: 'Rajdhani', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }

  tbody tr {
    border-bottom: 1px solid rgba(31,52,84,0.14);
    transition: background 0.15s;
  }

  tbody tr:nth-child(even) { background: var(--row-even); }
  tbody tr:nth-child(odd) { background: var(--row-odd); }
  tbody tr:hover { background: rgba(0,102,214,0.08); }

  td {
    padding: 12px 16px;
    vertical-align: middle;
  }

  .subnet-addr { color: var(--accent); font-weight: bold; }
  .netmask { color: #667b98; }
  .range { color: var(--text); font-size: 12px; }
  .binary { color: var(--muted); font-size: 11px; margin-top: 3px; }
  .usable { color: var(--green); }
  .hosts { color: var(--text); text-align: right; }

  .map-track {
    position: relative;
    width: 100%;
    height: 10px;
    border-radius: 10px;
    background: #e8eef8;
    overflow: hidden;
  }

  .map-segment {
    position: absolute;
    top: 0;
    height: 10px;
    border-radius: 10px;
    background: linear-gradient(90deg, rgba(0, 102, 214, 0.75) 0%, rgba(15, 157, 88, 0.75) 100%);
  }

  .bit-bar {
    margin-top: 6px;
    display: grid;
    grid-template-columns: repeat(32, minmax(0, 1fr));
    gap: 1px;
  }

  .bit {
    height: 7px;
    border-radius: 2px;
    background: #d8e2f0;
  }

  .bit.net {
    background: #2a7fe0;
  }

  .bit.host {
    background: #86b6eb;
  }

  .bit-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1px;
  }

  .depth-bar {
    display: inline-block;
    height: 3px;
    background: var(--accent);
    margin-bottom: 4px;
    opacity: 0.5;
    border-radius: 2px;
  }

  .error {
    background: #fff1f1;
    border: 1px solid #e8b3b3;
    color: #b53b3b;
    padding: 16px 24px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    margin-bottom: 24px;
  }

  .empty {
    text-align: center;
    padding: 60px;
    color: var(--muted);
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .tag {
    display: inline-block;
    font-size: 10px;
    padding: 2px 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .tag-net {
    background: rgba(0,102,214,0.1);
    border: 1px solid rgba(0,102,214,0.25);
    color: var(--accent);
  }

  .tag-bc {
    background: rgba(214,106,0,0.1);
    border: 1px solid rgba(214,106,0,0.25);
    color: var(--accent2);
  }

  .actions { display: flex; gap: 6px; align-items: center; }

  footer {
    margin-top: 40px;
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  @media (max-width: 768px) {
    h1 { font-size: 20px; }
    .input-panel { padding: 20px; }
    table { font-size: 11px; }
    td, th { padding: 8px 10px; }
    .summary-panel { grid-template-columns: repeat(2, minmax(130px, 1fr)); }
  }
</style>
</head>
<body>
<div class="scanlines"></div>
<div class="container">

  <header>
    <h1># SUBNET_CALCULATOR</h1>
    <span class="subtitle">Visual Network Partitioner</span>
  </header>

  <div class="input-panel">
    <div class="field">
      <label>Network Address</label>
      <input type="text" id="network" placeholder="192.168.1.0" value="192.168.0.0">
    </div>
    <div class="slash">/</div>
    <div class="field">
      <label>Mask Bits</label>
      <select id="mask">
        {% for i in range(8, 31) %}
        <option value="{{ i }}" {% if i == 24 %}selected{% endif %}>/{{ i }}</option>
        {% endfor %}
      </select>
    </div>
    <button class="btn-primary" onclick="calculate()">CALCULATE</button>
  </div>

  <div id="error-box" style="display:none" class="error"></div>

  <div class="summary-panel" id="summary-panel" style="display:none">
    <div class="summary-card">
      <div class="summary-label">Root CIDR</div>
      <div class="summary-value" id="sum-root">-</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Subnet Count</div>
      <div class="summary-value" id="sum-count">0</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Total Addresses</div>
      <div class="summary-value" id="sum-total">0</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">Address Type</div>
      <div class="summary-value" id="sum-type">-</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">IP Class</div>
      <div class="summary-value" id="sum-class">-</div>
    </div>
  </div>

  <div class="legend-panel" id="legend-panel" style="display:none">
    <span class="legend-title">Diagram Legend</span>
    <span class="legend-item"><span class="legend-chip address"></span>Address-space segment</span>
    <span class="legend-item"><span class="legend-chip network"></span>Network bits</span>
    <span class="legend-item"><span class="legend-chip host"></span>Host bits</span>
    <span class="legend-item"><span class="legend-chip vlan"></span>VLAN segment</span>
  </div>

  <div class="diagram-panel" id="network-diagram-panel" style="display:none">
    <div class="diagram-title">Network Diagram (Auto Updates On Split/Join)</div>
    <div class="diagram-track" id="network-diagram-track"></div>
    <div class="diagram-switch-wrap">
      <div class="diagram-switch-title">Switch Connectivity (VLAN Segregation)</div>
      <div id="switch-connectivity"></div>
    </div>
  </div>

  <div class="table-wrap" id="table-wrap" style="display:none">
    <table>
      <thead>
        <tr>
          <th>Subnet Address</th>
          <th>Netmask</th>
          <th>Range of Addresses</th>
          <th>Usable IPs</th>
          <th style="text-align:right">Hosts</th>
          <th>Visual Map</th>
          <th>Divide</th>
          <th>Join</th>
        </tr>
      </thead>
      <tbody id="subnet-body"></tbody>
    </table>
  </div>

  <footer>Built with Flask &amp; Python · ipaddress module</footer>
</div>

<script>
  let subnets = [];

  async function calculate() {
    const network = document.getElementById('network').value.trim();
    const mask = document.getElementById('mask').value;
    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ network, mask })
    });
    const data = await res.json();
    if (data.error) { showError(data.error); return; }
    subnets = data.subnets;
    render();
  }

  async function divideSubnet(idx) {
    const res = await fetch('/api/divide', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ subnets, index: idx })
    });
    const data = await res.json();
    if (data.error) { showError(data.error); return; }
    subnets = data.subnets;
    render();
  }

  async function joinSubnet(idx) {
    const res = await fetch('/api/join', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ subnets, index: idx })
    });
    const data = await res.json();
    if (data.error) { showError(data.error); return; }
    subnets = data.subnets;
    render();
  }

  function render() {
    document.getElementById('error-box').style.display = 'none';
    document.getElementById('summary-panel').style.display = 'grid';
    document.getElementById('legend-panel').style.display = 'flex';
    document.getElementById('network-diagram-panel').style.display = 'block';
    document.getElementById('table-wrap').style.display = 'block';
    const tbody = document.getElementById('subnet-body');
    tbody.innerHTML = '';

    const rootStart = Math.min(...subnets.map(s => s.network_int));
    const rootEnd = Math.max(...subnets.map(s => s.broadcast_int));
    const rootTotal = (rootEnd - rootStart) + 1;
    const rootPrefix = Math.max(0, 32 - Math.log2(rootTotal));
    const rootText = intToIp(rootStart) + '/' + rootPrefix;
    const rootMeta = subnets[0] || {};

    document.getElementById('sum-root').textContent = rootText;
    document.getElementById('sum-count').textContent = subnets.length.toLocaleString();
    document.getElementById('sum-total').textContent = rootTotal.toLocaleString();
    document.getElementById('sum-type').textContent = rootMeta.address_type || '-';
    document.getElementById('sum-class').textContent = rootMeta.ip_class || '-';

    renderNetworkDiagram(rootStart, rootTotal);

    subnets.forEach((s, i) => {
      const depth = s.prefix - s.base_prefix;
      const tr = document.createElement('tr');
      const left = ((s.network_int - rootStart) / rootTotal) * 100;
      const width = ((s.total_addresses / rootTotal) * 100);

      const canJoin = i > 0 && subnets[i-1].prefix === s.prefix && canSiblings(i);

      tr.innerHTML = `
        <td>
          <div style="margin-bottom:${depth>0?4:0}px">
            ${depth > 0 ? `<div class="depth-bar" style="width:${depth*14}px"></div>` : ''}
          </div>
          <span class="subnet-addr">${s.network}</span>
          <span style="color:var(--muted);font-size:11px"> /${s.prefix}</span>
        </td>
        <td class="netmask">${s.netmask}</td>
        <td class="range">
          ${s.first} <span style="color:var(--muted)">—</span> ${s.last}
          <div class="binary">Wildcard: ${s.wildcard}</div>
          <div class="binary">Mask(bin): ${s.netmask_binary}</div>
          <div style="margin-top:3px">
            <span class="tag tag-net">${s.network_addr}</span>
            <span class="tag tag-bc">${s.broadcast}</span>
          </div>
        </td>
        <td class="usable">${s.usable_first} — ${s.usable_last}</td>
        <td class="hosts">${s.hosts.toLocaleString()}</td>
        <td>
          <div class="map-track">
            <div class="map-segment" style="left:${left}%;width:${Math.max(width, 1.5)}%"></div>
          </div>
          ${buildBitDiagram(s.prefix)}
          <div class="binary">${s.cidr}</div>
        </td>
        <td>
          ${s.prefix < 30 ? `<button class="btn-divide" onclick="divideSubnet(${i})">÷ SPLIT</button>` : '<span style="color:var(--muted);font-size:11px">—</span>'}
        </td>
        <td>
          <button class="btn-join" onclick="joinSubnet(${i})" ${!canJoin ? 'disabled' : ''}>⊕ JOIN</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  function canSiblings(idx) {
    if (idx === 0) return false;
    const a = subnets[idx - 1];
    const b = subnets[idx];
    if (a.prefix !== b.prefix) return false;
    // Check they are adjacent and form a valid pair
    return true;
  }

  function showError(msg) {
    const box = document.getElementById('error-box');
    box.textContent = '⚠ ' + msg;
    box.style.display = 'block';
  }

  function buildBitDiagram(prefix) {
    const bits = [];
    for (let i = 0; i < 32; i++) {
      const cls = i < prefix ? 'net' : 'host';
      bits.push(`<span class="bit ${cls}"></span>`);
    }
    return `
      <div class="bit-bar">${bits.join('')}</div>
      <div class="bit-labels">
        <span>N:${prefix}</span>
        <span>H:${32 - prefix}</span>
      </div>
    `;
  }

  function renderNetworkDiagram(rootStart, rootTotal) {
    const track = document.getElementById('network-diagram-track');
    track.innerHTML = '';

    subnets.forEach((s, idx) => {
      const left = ((s.network_int - rootStart) / rootTotal) * 100;
      const width = Math.max((s.total_addresses / rootTotal) * 100, 1);
      const depth = s.prefix - s.base_prefix;
      const vlanId = getVlanId(s, idx);

      const block = document.createElement('div');
      block.className = 'diagram-block';
      block.style.left = `${left}%`;
      block.style.width = `${width}%`;
      block.style.background = vlanColor(vlanId, depth);
      block.title = `VLAN ${vlanId} · ${s.cidr} (${s.total_addresses.toLocaleString()} addresses)`;

      if (width >= 10) {
        block.innerHTML = `
          <div class="diagram-block-label">VLAN ${vlanId} · ${s.network}/${s.prefix}</div>
          <div class="diagram-block-meta">${s.total_addresses.toLocaleString()} addrs</div>
        `;
      }

      track.appendChild(block);
    });

    renderSwitchConnectivity();
  }

  function depthColor(depth) {
    const hue = 210 - Math.min(depth * 18, 80);
    return `hsl(${hue}, 72%, 50%)`;
  }

  function getVlanId(subnet, idx) {
    const octets = subnet.network.split('.').map(Number);
    const depth = subnet.prefix - subnet.base_prefix;
    const seed = (octets[2] + octets[3] + subnet.prefix + (depth * 7) + idx) % 6;
    return 10 + (seed * 10);
  }

  function vlanColor(vlanId, depth) {
    const baseHue = (vlanId * 3) % 360;
    const light = 48 + Math.min(depth * 3, 14);
    return `hsl(${baseHue}, 72%, ${light}%)`;
  }

  function renderSwitchConnectivity() {
    const container = document.getElementById('switch-connectivity');
    const vlanGroups = groupSubnetsByVlan();
    const vlans = Object.keys(vlanGroups).sort((a, b) => Number(a) - Number(b));

    if (!vlans.length) {
      container.innerHTML = '';
      return;
    }

    const width = Math.max(880, vlans.length * 150);
    const height = 220;
    const centerX = width / 2;
    const coreY = 24;
    const accessY = 116;
    const leftPad = 70;
    const rightPad = 70;
    const span = Math.max(1, vlans.length - 1);

    const nodes = vlans.map((vlan, i) => {
      const x = vlans.length === 1
        ? centerX
        : leftPad + ((width - leftPad - rightPad) * (i / span));
      return { vlan, x, subnets: vlanGroups[vlan] };
    });

    let svg = `<svg class="switch-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
    svg += `<defs>
      <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
        <feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="#5f738f" flood-opacity="0.25"/>
      </filter>
    </defs>`;

    nodes.forEach((node) => {
      svg += `<line x1="${centerX}" y1="${coreY + 28}" x2="${node.x}" y2="${accessY - 4}" stroke="#94a9c6" stroke-width="2" />`;
    });

    svg += `<rect x="${centerX - 74}" y="${coreY}" width="148" height="34" rx="8" fill="#1b4f96" filter="url(#softShadow)"/>`;
    svg += `<text x="${centerX}" y="${coreY + 21}" text-anchor="middle" font-size="12" fill="#ffffff" font-family="Rajdhani, sans-serif">CORE SWITCH</text>`;

    nodes.forEach((node) => {
      const hue = (Number(node.vlan) * 3) % 360;
      const subnetCount = node.subnets.length;
      const sample = node.subnets.slice(0, 2).map((s) => s.cidr).join(' | ');

      svg += `<rect x="${node.x - 62}" y="${accessY}" width="124" height="62" rx="8" fill="hsl(${hue},72%,46%)" filter="url(#softShadow)"/>`;
      svg += `<text x="${node.x}" y="${accessY + 18}" text-anchor="middle" font-size="12" fill="#ffffff" font-family="Share Tech Mono, monospace">SW VLAN ${node.vlan}</text>`;
      svg += `<text x="${node.x}" y="${accessY + 34}" text-anchor="middle" font-size="10" fill="#ecf4ff" font-family="Rajdhani, sans-serif">${subnetCount} subnet${subnetCount > 1 ? 's' : ''}</text>`;
      svg += `<text x="${node.x}" y="${accessY + 49}" text-anchor="middle" font-size="9" fill="#ecf4ff" font-family="Share Tech Mono, monospace">${escapeSvg(sample)}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  function groupSubnetsByVlan() {
    return subnets.reduce((acc, s, idx) => {
      const vlan = getVlanId(s, idx);
      if (!acc[vlan]) acc[vlan] = [];
      acc[vlan].push(s);
      return acc;
    }, {});
  }

  function escapeSvg(text) {
    return text
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function intToIp(num) {
    return [
      (num >>> 24) & 255,
      (num >>> 16) & 255,
      (num >>> 8) & 255,
      num & 255
    ].join('.');
  }

  // Auto-calculate on load
  calculate();
</script>
</body>
</html>
"""

def subnet_to_dict(net, base_prefix):
  hosts = net.num_addresses - 2 if net.prefixlen < 31 else net.num_addresses
  hosts = max(0, hosts)
  all_hosts = list(net.hosts())
  usable_first = str(all_hosts[0]) if all_hosts else str(net.network_address)
  usable_last = str(all_hosts[-1]) if all_hosts else str(net.broadcast_address)
  address_type = "Private" if net.is_private else "Public/Special"
  return {
    "network": str(net.network_address),
    "prefix": net.prefixlen,
    "base_prefix": base_prefix,
    "netmask": str(net.netmask),
    "netmask_binary": mask_to_binary(net.netmask),
    "wildcard": str(net.hostmask),
    "first": str(net.network_address),
    "last": str(net.broadcast_address),
    "network_addr": str(net.network_address),
    "broadcast": str(net.broadcast_address),
    "usable_first": usable_first,
    "usable_last": usable_last,
    "hosts": hosts,
    "total_addresses": net.num_addresses,
    "ip_class": ipv4_class(net.network_address),
    "address_type": address_type,
    "network_int": int(net.network_address),
    "broadcast_int": int(net.broadcast_address),
    "cidr": str(net)
  }

@app.route('/')
def index():
    return render_template_string(HTML, range=range)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        cidr = f"{data['network']}/{data['mask']}"
        net = ipaddress.ip_network(cidr, strict=False)
        base = net.prefixlen
        return jsonify({"subnets": [subnet_to_dict(net, base)]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/divide', methods=['POST'])
def divide():
    data = request.json
    subnets = data['subnets']
    idx = data['index']
    try:
        s = subnets[idx]
        net = ipaddress.ip_network(f"{s['network']}/{s['prefix']}", strict=False)
        if net.prefixlen >= 30:
            return jsonify({"error": "Cannot divide further (prefix >= /30)"})
        children = list(net.subnets(prefixlen_diff=1))
        base = s['base_prefix']
        new_subnets = (
            subnets[:idx] +
            [subnet_to_dict(children[0], base), subnet_to_dict(children[1], base)] +
            subnets[idx+1:]
        )
        return jsonify({"subnets": new_subnets})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/join', methods=['POST'])
def join():
    data = request.json
    subnets = data['subnets']
    idx = data['index']
    try:
        if idx == 0:
            return jsonify({"error": "Nothing to join above this subnet"})
        a = subnets[idx - 1]
        b = subnets[idx]
        if a['prefix'] != b['prefix']:
            return jsonify({"error": "Subnets must be the same size to join"})
        net_a = ipaddress.ip_network(f"{a['network']}/{a['prefix']}", strict=False)
        net_b = ipaddress.ip_network(f"{b['network']}/{b['prefix']}", strict=False)
        parent = net_a.supernet()
        if list(parent.subnets()) != [net_a, net_b]:
            return jsonify({"error": "These subnets are not siblings — cannot join"})
        base = a['base_prefix']
        merged = subnet_to_dict(parent, base)
        new_subnets = subnets[:idx-1] + [merged] + subnets[idx+1:]
        return jsonify({"subnets": new_subnets})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
  debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
  port = int(os.getenv('PORT', '5000'))
  app.run(debug=debug_mode, host='0.0.0.0', port=port)
