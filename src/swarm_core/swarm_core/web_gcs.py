#!/usr/bin/env python3
"""
Teknofest Autonomous Swarm Ground Control Station (Web GCS v3)
Lightweight, zero-external-dependency web-based tactical dashboard.
Provides real-time radar mapping, interactive target placement,
fleet role allocation, multi-hop mesh visualization, and mission controls.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from swarm_core.algorithms import Vector3, AuctionTaskAllocator
from swarm_core.mesh_network import DecentralizedMeshNetwork

# Shared State
SWARM_STATE = {
    "mission_mode": "FORMATION",
    "formation_type": "V_SHAPE",
    "leader_id": 1,
    "geofence": {"xmin": -50.0, "xmax": 50.0, "ymin": -50.0, "ymax": 50.0, "zmax": 30.0},
    "referee": {
        "score": 1150.0,
        "base_score": 1000.0,
        "penalties": 0.0,
        "bonuses": 150.0,
        "status": "OPERASYONEL / KURAL İHLALİ YOK"
    },
    "sensor_fusion": {
        "mode": "EKF_ACTIVE",
        "gnss_status": "3D_FIX_OK",
        "uncertainty_1sigma": 0.28
    },
    "collision_avoidance": "RVO_3D_ENABLED",
    "drones": {
        "1": {"x": 0.0, "y": 0.0, "z": 12.0, "vx": 0.0, "vy": 0.0, "battery": 96.0, "role": "LEADER / RELAY", "time": time.time()},
        "2": {"x": 10.0, "y": 8.0, "z": 10.0, "vx": 0.0, "vy": 0.0, "battery": 94.5, "role": "SCOUT", "time": time.time()},
        "3": {"x": -2.8, "y": -2.0, "z": 10.0, "vx": 0.0, "vy": 0.0, "battery": 95.0, "role": "INTERCEPTOR", "time": time.time()},
        "4": {"x": -5.6, "y": 4.0, "z": 10.0, "vx": 0.0, "vy": 0.0, "battery": 92.0, "role": "INTERCEPTOR", "time": time.time()},
        "5": {"x": -5.6, "y": -4.0, "z": 10.0, "vx": 0.0, "vy": 0.0, "battery": 93.5, "role": "RESERVE", "time": time.time()}
    },
    "targets": [
        {"id": "TARGET_ALPHA", "x": 20.0, "y": 25.0, "assigned_uav": 3, "confirmed": True}
    ],
    "logs": [
        "Sistem başlatıldı: 5 Heterojen İHA operasyonel",
        "Formasyon kilidi aktif: V_SHAPE",
        "Ad-hoc Mesh Ağı devrede (OLSR Multi-hop)"
    ]
}

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEKNOFEST SÜRÜ ZEKASI | KOMUTA MERKEZİ (GCS v3)</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #131b2e;
            --accent-cyan: #00E5FF;
            --accent-blue: #2979FF;
            --accent-green: #00E676;
            --accent-red: #FF1744;
            --accent-gold: #FFD700;
            --text-main: #E0E6ED;
            --text-dim: #78909C;
            --border-color: #1e293b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg-color); color: var(--text-main); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        header {
            background: linear-gradient(90deg, #09101d, #14223d);
            border-bottom: 2px solid var(--accent-cyan);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 { font-size: 1.25rem; letter-spacing: 1.5px; color: var(--accent-cyan); display: flex; align-items: center; gap: 10px; }
        .status-badge { background: rgba(0,229,255,0.1); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; }
        
        .main-container { display: flex; flex: 1; gap: 16px; padding: 16px; overflow: hidden; }
        .radar-section { flex: 2; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; display: flex; flex-direction: column; }
        .radar-header { padding: 10px 16px; border-bottom: 1px solid var(--border-color); font-weight: bold; color: var(--accent-cyan); display: flex; justify-content: space-between; }
        canvas { flex: 1; width: 100%; height: 100%; background: radial-gradient(circle at center, #111a2e 0%, #080d1a 100%); cursor: crosshair; }
        
        .side-section { flex: 1.2; display: flex; flex-direction: column; gap: 16px; }
        .panel { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; }
        .panel-title { font-size: 0.9rem; font-weight: bold; color: var(--accent-cyan); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
        
        .controls-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        button {
            background: #1e293b; color: var(--text-main); border: 1px solid #334155; padding: 10px; border-radius: 6px;
            font-size: 0.85rem; font-weight: bold; cursor: pointer; transition: all 0.2s;
        }
        button:hover { background: var(--accent-blue); border-color: var(--accent-cyan); color: #fff; }
        button.danger:hover { background: var(--accent-red); }
        
        .drone-list { display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; }
        .drone-card {
            background: #0f172a; border-left: 3px solid var(--accent-green); padding: 8px 12px; border-radius: 4px;
            display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem;
        }
        .drone-card.leader { border-left-color: var(--accent-gold); }
        
        .log-box {
            background: #090e17; border: 1px solid #1a2333; border-radius: 4px; padding: 8px; font-size: 0.78rem;
            color: #90a4ae; height: 120px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px;
        }
    </style>
</head>
<body>
    <header>
        <h1>🚁 TEKNOFEST SÜRÜ ZEKASI KOMUTA MERKEZİ</h1>
        <div style="display:flex; gap:12px; align-items:center;">
            <span class="status-badge" id="referee-badge" style="border-color:var(--accent-green); color:var(--accent-green);">🏆 PUAN: 1150 PTS</span>
            <span class="status-badge" id="fusion-badge" style="border-color:var(--accent-cyan); color:var(--accent-cyan);">🛰️ EKF: 3D FIX (0.28m σ)</span>
            <span class="status-badge" id="rvo-badge" style="border-color:#bb86fc; color:#bb86fc;">⚡ RVO-3D: AKTİF</span>
            <span class="status-badge" id="mode-badge">MOD: FORMATION</span>
            <span class="status-badge" id="leader-badge" style="border-color:var(--accent-gold); color:var(--accent-gold);">LİDER: UAV-1</span>
        </div>
    </header>

    <div class="main-container">
        <div class="radar-section">
            <div class="radar-header">
                <span>🛰️ TAKTİKSEL RADAR (Hedef Eklemek İçin Radara Tıklayın)</span>
                <span id="centroid-coords" style="color:var(--text-dim); font-size:0.85rem;">Merkez: X=0.0m Y=0.0m</span>
            </div>
            <canvas id="radarCanvas"></canvas>
        </div>

        <div class="side-section">
            <div class="panel">
                <div class="panel-title">🎮 Görev ve Formasyon Kontrolü</div>
                <div class="controls-grid">
                    <button onclick="setMode('V_SHAPE')">V Formasyonu</button>
                    <button onclick="setMode('LINE')">Hat Formasyonu</button>
                    <button onclick="setMode('CIRCLE')">Çember Formasyonu</button>
                    <button onclick="setMode('GRID')">Matris Formasyonu</button>
                    <button onclick="setMission('SEARCH')">🔍 Keşif Spirali</button>
                    <button onclick="setMission('BOIDS')">Boids Flocking</button>
                    <button class="danger" style="grid-column: span 2;" onclick="setMission('RTL')">⚠️ ACİL EVE DÖN (RTL)</button>
                </div>
            </div>

            <div class="panel">
                <div class="panel-title">📡 Heterojen Sürü Filosu & Mesh Durumu</div>
                <div class="drone-list" id="droneList"></div>
            </div>

            <div class="panel">
                <div class="panel-title">📜 Taktiksel Görev ve Olay Kaydı</div>
                <div class="log-box" id="logBox"></div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('radarCanvas');
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight - 40;
        }
        window.addEventListener('resize', resize);
        resize();

        // Click canvas to drop target
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const scale = Math.min(canvas.width, canvas.height) / 110;

            const targetX = (clickX - cx) / scale;
            const targetY = (cy - clickY) / scale;

            const targetId = `TARGET_${Math.floor(Math.random()*900 + 100)}`;
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({add_target: {id: targetId, x: targetX, y: targetY}})
            });
        });

        function drawRadar(data) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const scale = Math.min(canvas.width, canvas.height) / 110;

            // Draw radar range rings
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            for (let r = 10; r <= 50; r += 10) {
                ctx.beginPath();
                ctx.arc(cx, cy, r * scale, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Crosshairs
            ctx.beginPath();
            ctx.moveTo(cx, 0); ctx.lineTo(cx, canvas.height);
            ctx.moveTo(0, cy); ctx.lineTo(canvas.width, cy);
            ctx.stroke();

            // Geofence boundary
            ctx.strokeStyle = '#00E5FF';
            ctx.setLineDash([6, 6]);
            ctx.strokeRect(cx - 50 * scale, cy - 50 * scale, 100 * scale, 100 * scale);
            ctx.setLineDash([]);

            // Draw Targets & Interception Lines
            if (data.targets) {
                data.targets.forEach(t => {
                    const tx = cx + t.x * scale;
                    const ty = cy - t.y * scale;

                    // Crosshair target
                    ctx.strokeStyle = '#FF1744';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(tx, ty, 9, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.fillStyle = '#FF1744';
                    ctx.font = '11px monospace';
                    ctx.fillText(t.id, tx + 12, ty + 4);

                    // Draw line from assigned UAV if available
                    if (t.assigned_uav && data.drones[t.assigned_uav]) {
                        const ad = data.drones[t.assigned_uav];
                        ctx.strokeStyle = 'rgba(255, 23, 68, 0.4)';
                        ctx.setLineDash([4, 4]);
                        ctx.beginPath();
                        ctx.moveTo(cx + ad.x * scale, cy - ad.y * scale);
                        ctx.lineTo(tx, ty);
                        ctx.stroke();
                        ctx.setLineDash([]);
                    }
                });
            }

            // Draw Multi-Hop Mesh Links
            const drones = Object.entries(data.drones || {});
            ctx.strokeStyle = 'rgba(0, 229, 255, 0.25)';
            ctx.lineWidth = 1.5;
            for (let i = 0; i < drones.length; i++) {
                for (let j = i + 1; j < drones.length; j++) {
                    const d1 = drones[i][1];
                    const d2 = drones[j][1];
                    const dist = Math.hypot(d1.x - d2.x, d1.y - d2.y);
                    if (dist < 35.0) {
                        ctx.beginPath();
                        ctx.moveTo(cx + d1.x * scale, cy - d1.y * scale);
                        ctx.lineTo(cx + d2.x * scale, cy - d2.y * scale);
                        ctx.stroke();
                    }
                }
            }

            // Draw Drones
            drones.forEach(([id, d]) => {
                const dx = cx + d.x * scale;
                const dy = cy - d.y * scale;
                const isLeader = (parseInt(id) === data.leader_id);

                ctx.fillStyle = isLeader ? '#FFD700' : (d.role && d.role.includes('SCOUT') ? '#00E676' : '#00E5FF');
                ctx.beginPath();
                ctx.arc(dx, dy, isLeader ? 7 : 5, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#ffffff';
                ctx.font = '11px monospace';
                ctx.fillText(`UAV-${id}`, dx + 8, dy - 6);
            });
        }

        async function updateTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                const data = await res.json();

                drawRadar(data);

                document.getElementById('mode-badge').innerText = `MOD: ${data.mission_mode} (${data.formation_type})`;
                document.getElementById('leader-badge').innerText = `LİDER: UAV-${data.leader_id}`;

                if (data.referee) {
                    document.getElementById('referee-badge').innerText = `🏆 PUAN: ${data.referee.score} PTS`;
                }
                if (data.sensor_fusion) {
                    document.getElementById('fusion-badge').innerText = `🛰️ EKF: ${data.sensor_fusion.gnss_status} (${data.sensor_fusion.uncertainty_1sigma}m σ)`;
                }

                // Update drone list
                const list = document.getElementById('droneList');
                list.innerHTML = '';
                Object.entries(data.drones || {}).forEach(([id, d]) => {
                    const isLeader = (parseInt(id) === data.leader_id);
                    const card = document.createElement('div');
                    card.className = `drone-card ${isLeader ? 'leader' : ''}`;
                    card.innerHTML = `
                        <div>
                            <strong>${isLeader ? '👑 ' : ''}UAV-${id} <span style="font-size:0.75rem; color:#00E5FF;">[${d.role || 'STANDARD'}]</span></strong>
                            <div style="font-size:0.75rem; color:#90a4ae;">X:${d.x.toFixed(1)} Y:${d.y.toFixed(1)} Z:${d.z.toFixed(1)}m</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:${d.battery > 30 ? '#00E676' : '#FF1744'}; font-weight:bold;">⚡ ${d.battery.toFixed(0)}%</span>
                        </div>
                    `;
                    list.appendChild(card);
                });

                // Update logs
                const logBox = document.getElementById('logBox');
                logBox.innerHTML = (data.logs || []).map(l => `<div>› ${l}</div>`).join('');
            } catch (err) {
                console.error(err);
            }
        }

        function setMode(type) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mission_mode: 'FORMATION', formation_type: type})
            });
        }

        function setMission(mode) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mission_mode: mode})
            });
        }

        setInterval(updateTelemetry, 500);
        updateTelemetry();
    </script>
</body>
</html>
"""


class GCSRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode('utf-8'))
        elif parsed.path == '/api/telemetry':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(SWARM_STATE).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/command':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                cmd = json.loads(body.decode('utf-8'))
                if "mission_mode" in cmd:
                    SWARM_STATE["mission_mode"] = cmd["mission_mode"]
                if "formation_type" in cmd:
                    SWARM_STATE["formation_type"] = cmd["formation_type"]

                if "add_target" in cmd:
                    t = cmd["add_target"]
                    allocator = AuctionTaskAllocator()
                    allocator.add_task(t["id"], Vector3(t["x"], t["y"], 0.0))
                    fleet = {
                        int(k): {'pos': Vector3(v['x'], v['y'], v['z']), 'battery': v['battery']}
                        for k, v in SWARM_STATE["drones"].items()
                    }
                    assignments = allocator.allocate_tasks(fleet)
                    assigned_uav = assignments.get(t["id"], 3)
                    t["assigned_uav"] = assigned_uav
                    t["confirmed"] = True
                    SWARM_STATE["targets"].append(t)
                    SWARM_STATE["logs"].append(f"Yeni Hedef: {t['id']} -> MATA İhalesi: UAV-{assigned_uav}")

                if len(SWARM_STATE["logs"]) > 20:
                    SWARM_STATE["logs"].pop(0)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"SUCCESS"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def start_server(port: int = 8080):
    server = HTTPServer(('0.0.0.0', port), GCSRequestHandler)
    print("=" * 65)
    print(f"🚀 TEKNOFEST SÜRÜ ZEKASI GCS YER İSTASYONU (v3) AKTİF!")
    print(f"🔗 Tarayıcıdan açın: http://localhost:{port}")
    print("=" * 65)
    server.serve_forever()


def main():
    start_server(8080)


if __name__ == '__main__':
    main()
