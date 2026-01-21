// =============================================================
// PLAYER STATE
// =============================================================

let playlist = [];
let index = 0;

let deviceId = null;
let token = null;

let ws = null;
let reconnectTimer = null;
let playTimeout = null;

// DOM
const imgEl = document.getElementById("image-player");
const vidEl = document.getElementById("video-player");

// Emergency
let emergencyOverlay = null;

// =============================================================
// PLAYLIST NORMALIZATION (MATCHES API)
// =============================================================

function normalizeItem(item) {
    if (!item || !item.media) return null;

    const url = item.media.url;
    const mime = item.media.mime_type;

    if (!url || !mime) return null;

    const type = mime.startsWith("video") ? "video" : "image";

    return {
        type,
        url,
        duration: item.duration_seconds || 5
    };
}

// =============================================================
// PLAYBACK LOOP (SAFE, NON-RECURSIVE)
// =============================================================

function playNext() {
    clearTimeout(playTimeout);

    if (!playlist.length) {
        console.warn("[PLAYER] Playlist empty");
        return;
    }

    let attempts = 0;

    while (attempts < playlist.length) {
        const raw = playlist[index];
        index = (index + 1) % playlist.length;
        attempts++;

        const item = normalizeItem(raw);
        if (!item) {
            console.warn("[PLAYER] Skipping invalid item:", raw);
            continue;
        }

        console.log("[PLAYER] Playing:", item);

        if (item.type === "image") {
            playImage(item);
            return;
        }

        if (item.type === "video") {
            playVideo(item);
            return;
        }
    }

    console.error("[PLAYER] No playable items found");
}

function playImage(item) {
    vidEl.pause();
    vidEl.onended = null;
    vidEl.style.display = "none";

    imgEl.src = item.url;
    imgEl.style.display = "block";

    playTimeout = setTimeout(playNext, item.duration * 1000);
}

function playVideo(item) {
    imgEl.style.display = "none";

    vidEl.src = item.url;
    vidEl.style.display = "block";
    vidEl.onended = playNext;

    vidEl.play().catch(err => {
        console.warn("[VIDEO] Autoplay blocked, retrying", err);
        setTimeout(() => vidEl.play(), 500);
    });
}

// =============================================================
// PLAYBACK CONTROLS
// =============================================================

function pausePlayback() {
    console.log("[PLAYER] Pause");
    clearTimeout(playTimeout);
    vidEl.pause();
}

function resumePlayback() {
    console.log("[PLAYER] Play");

    if (vidEl.style.display === "block") {
        vidEl.play().catch(() => {});
    } else {
        playNext();
    }
}

function stopPlayback() {
    console.log("[PLAYER] Stop");
    clearTimeout(playTimeout);

    vidEl.onended = null;
    vidEl.pause();

    imgEl.src = "";
    vidEl.src = "";
    vidEl.load();    

    imgEl.style.display = "none";
    vidEl.style.display = "none";
}

// =============================================================
// EMERGENCY MODE
// =============================================================

function showEmergency(payload) {
    console.log("[EMERGENCY] SHOW");

    stopPlayback();

    if (!emergencyOverlay) {
        emergencyOverlay = document.createElement("div");
        emergencyOverlay.id = "emergency-overlay";
        emergencyOverlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: red;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4vw;
            z-index: 9999;
            text-align: center;
            padding: 2rem;
        `;
        document.body.appendChild(emergencyOverlay);
    }

    emergencyOverlay.textContent =
        payload?.message || "EMERGENCY";
}

function hideEmergency() {
    console.log("[EMERGENCY] HIDE");

    if (emergencyOverlay) {
        emergencyOverlay.remove();
        emergencyOverlay = null;
    }

    playNext();
}

// =============================================================
// DEVICE-LEVEL COMMANDS (BROWSER SAFE)
// =============================================================

function rebootDevice() {
    console.warn("[DEVICE] Reboot requested");
    location.reload();
}

function shutdownDevice() {
    console.warn("[DEVICE] Shutdown requested");
    stopPlayback();
    document.body.style.background = "black";
}

// =============================================================
// COMMAND ROUTER (MATCHES DeviceCommandEnum)
// =============================================================

function handleDeviceCommand(cmd) {
    if (!cmd || !cmd.type) return;

    console.log("[CMD] Received:", cmd.type);

    switch (cmd.type) {
        case "reload_playlist":
            reloadPlaylist();
            break;

        case "play":
            resumePlayback();
            break;

        case "pause":
            pausePlayback();
            break;

        case "stop":
            stopPlayback();
            break;

        case "emergency_show":
            showEmergency(cmd.payload);
            break;

        case "emergency_hide":
            hideEmergency();
            break;

        case "ping":
            console.log("[CMD] ping");
            break;

        case "reboot":
            rebootDevice();
            break;

        case "shutdown":
            shutdownDevice();
            break;
        

        case "revoke":
            console.warn("[DEVICE] REVOKED");

            stopPlayback();

            // close websocket
            try {
                ws?.close();
            } catch {}

            // show revoked screen
            document.body.innerHTML = `
                <div style="
                    background:black;
                    color:white;
                    height:100vh;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:2rem;
                    font-family:Arial;
                ">
                    Device revoked by administrator
                </div>
            `;

            return;


        default:
            console.warn("[CMD] Unknown command:", cmd.type);
    }
}

// =============================================================
// PLAYLIST RELOAD
// =============================================================

async function reloadPlaylist() {
    console.log("[CMD] Reloading playlist");

    try {
        if (emergencyOverlay) {
            emergencyOverlay.remove();
            emergencyOverlay = null;
        }

        clearTimeout(playTimeout);
        vidEl.pause();

        const res = await fetch(`/api/v1/devices/${deviceId}/playback`);
        if (!res.ok) throw new Error("Playback reload failed");

        const data = await res.json();
        playlist = data.items || [];
        index = 0;

        playNext();
    } catch (e) {
        console.error("[CMD] Reload failed", e);
    }
}

// =============================================================
// WEBSOCKET (ENTERPRISE-GRADE)
// =============================================================

function getWebSocketUrl(token) {
    const { protocol, host } = window.location;
    const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
    return `${wsProtocol}//${host}/api/v1/ws/device?token=${encodeURIComponent(token)}`;
}

function connectWebSocket() {
    if (!token || token === "null" || token === "undefined") {
        console.error("[WS] Invalid or missing token, not connecting:", token);
        return;
    }

    const url = getWebSocketUrl(token);
    console.log("[WS] Connecting:", url);

    ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("[WS] Connected");
        clearTimeout(reconnectTimer);
    };

    ws.onmessage = (event) => {
        let msg;
        try {
            msg = JSON.parse(event.data);
        } catch {
            return;
        }
        handleDeviceCommand(msg);
    };

    ws.onclose = () => {
        console.warn("[WS] Disconnected — retry in 10s");
        reconnectTimer = setTimeout(connectWebSocket, 10000);
    };

    ws.onerror = () => ws.close();
}

// =============================================================
// ENTRY POINT (CALLED FROM boot.js ONLY)
// =============================================================

window.startPlayer = function (deviceIdParam, tokenParam) {
    if (!deviceIdParam || !tokenParam) {
        console.error("[PLAYER] startPlayer called without valid deviceId/token", {
            deviceIdParam,
            tokenParam
        });
        return;
    }

    deviceId = deviceIdParam;
    token = tokenParam;

    playlist = window.__PLAYLIST__ || [];
    index = 0;

    console.log("[PLAYER] Starting with token:", token);
    console.log("[PLAYER] Playlist loaded:", playlist);

    playNext();
    connectWebSocket();
};
