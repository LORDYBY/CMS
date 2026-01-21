// // -------------------------------------------------------------
// // DEVICE BOOT PROCESS (MATCHES BACKEND CONTRACT)
// // -------------------------------------------------------------

// async function generateFingerprint() {
//     return btoa([
//         navigator.userAgent,
//         screen.width + "x" + screen.height,
//         Intl.DateTimeFormat().resolvedOptions().timeZone
//     ].join("|"));
// }

// // -------------------------------------------------------------
// // DEVICE REGISTRATION (FIRST BOOT ONLY)
// // -------------------------------------------------------------

// async function registerDevice() {
//     console.log("[BOOT] Registering device...");

//     const fingerprint = await generateFingerprint();

//     const res = await fetch("/api/v1/devices/register", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ fingerprint })
//     });

//     if (!res.ok) {
//         throw new Error("Device registration failed");
//     }

//     const data = await res.json();
//     console.log("[BOOT] Registration:", data);

//     // Always store device_id
//     localStorage.setItem("device_id", data.device_id);

//     // Store token ONLY if backend returned one (first registration)
//     if (data.token) {
//         localStorage.setItem("device_token", data.token);
//     }

//     return data;
// }

// // -------------------------------------------------------------
// // WAIT FOR APPROVAL (POLLING)
// // -------------------------------------------------------------

// async function waitForApproval(deviceId) {
//     console.log("[BOOT] Waiting for approval...");
//     document.getElementById("loading").textContent =
//         "Awaiting device approval…";

//     while (true) {
//         const res = await fetch(`/api/v1/devices/${deviceId}/status`);
//         if (!res.ok) {
//             throw new Error("Status check failed");
//         }

//         const data = await res.json();
//         console.log("[BOOT] Status:", data);

//         if (data.state === "APPROVED" || data.state === "ACTIVE") {
//             console.log("[BOOT] Device approved");
//             return;
//         }

//         await new Promise(r => setTimeout(r, 5000));
//     }
// }

// // -------------------------------------------------------------
// // LOAD PLAYLIST
// // -------------------------------------------------------------

// async function loadPlayback(deviceId) {
//     console.log("[BOOT] Loading playlist...");

//     const res = await fetch(`/api/v1/devices/${deviceId}/playback`);
//     if (!res.ok) {
//         throw new Error("Playback fetch failed");
//     }

//     const data = await res.json();
//     return data.items || [];
// }

// // -------------------------------------------------------------
// // PROVISIONING / RECOVERY SCREEN
// // -------------------------------------------------------------

// function showProvisioningScreen(deviceId) {
//     document.body.innerHTML = `
//         <div style="
//             display:flex;
//             flex-direction:column;
//             align-items:center;
//             justify-content:center;
//             height:100vh;
//             background:#000;
//             color:#fff;
//             text-align:center;
//         ">
//             <div style="font-size:2.2rem;">
//                 Device not provisioned
//             </div>

//             <div style="margin-top:1.5rem;font-size:1.3rem;">
//                 Device ID:
//             </div>

//             <code style="
//                 margin-top:0.5rem;
//                 font-size:1rem;
//                 background:#111;
//                 padding:0.5rem 1rem;
//                 border-radius:6px;
//             ">
//                 ${deviceId}
//             </code>

//             <div style="margin-top:2rem;font-size:1rem;opacity:0.8;">
//                 Please approve this device in the admin panel
//             </div>
//         </div>
//     `;
// }

// // -------------------------------------------------------------
// // MAIN BOOT ENTRY
// // -------------------------------------------------------------

// window.bootDevice = async function () {
//     console.log("[BOOT] Starting...");

//     let deviceId = localStorage.getItem("device_id");
//     let token = localStorage.getItem("device_token");

//     // ---------------------------------------------------------
//     // CASE 1: device exists BUT token is missing
//     // → unrecoverable → provisioning screen
//     // ---------------------------------------------------------
//     if (deviceId && !token) {
//         console.warn("[BOOT] Device ID exists but token is missing");
//         showProvisioningScreen(deviceId);
//         return;
//     }

//     // ---------------------------------------------------------
//     // CASE 2: first-ever boot (no device_id)
//     // ---------------------------------------------------------
//     if (!deviceId) {
//         const reg = await registerDevice();
//         deviceId = reg.device_id;
//         token = reg.token || null;

//         if (!token) {
//             console.warn("[BOOT] Registration returned no token");
//             showProvisioningScreen(deviceId);
//             return;
//         }
//     }

//     // ---------------------------------------------------------
//     // WAIT FOR ADMIN APPROVAL
//     // ---------------------------------------------------------
//     await waitForApproval(deviceId);

//     // ---------------------------------------------------------
//     // LOAD PLAYLIST
//     // ---------------------------------------------------------
//     const playlist = await loadPlayback(deviceId);
//     window.__PLAYLIST__ = playlist;

//     console.log("[BOOT] Playlist ready:", playlist);
//     console.log("[BOOT] Using token:", token);

//     document.getElementById("loading").style.display = "none";

//     // ---------------------------------------------------------
//     // START PLAYER (SAFE, ONCE)
//     // ---------------------------------------------------------
//     window.startPlayer(deviceId, token);
// };

// // -------------------------------------------------------------
// // APP ENTRY
// // -------------------------------------------------------------

// window.addEventListener("load", () => {
//     if ("serviceWorker" in navigator) {
//         navigator.serviceWorker.register("service-worker.js");
//     }
//     window.bootDevice();
// });
// =============================================================



// =============================================================
// DIGITAL SIGNAGE — DEVICE BOOT (PRODUCTION SAFE)
// =============================================================

async function generateFingerprint() {
    return btoa([
        navigator.userAgent,
        screen.width + "x" + screen.height,
        Intl.DateTimeFormat().resolvedOptions().timeZone
    ].join("|"));
}

function showProvisioningScreen(deviceId) {
    document.body.innerHTML = `
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            height:100vh;
            background:#000;
            color:#fff;
            text-align:center;
            font-family:Arial;
        ">
            <div style="font-size:2.2rem;">Device awaiting approval</div>
            <code style="margin-top:1rem">${deviceId}</code>
        </div>
    `;
}

function showRevokedScreen() {
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
            This device has been revoked
        </div>
    `;
}

// -------------------------------------------------------------
// MAIN BOOT
// -------------------------------------------------------------
window.bootDevice = async function () {
    console.log("[BOOT] Starting device...");

    try {
        const fingerprint = await generateFingerprint();

        // -----------------------------------------------------
        // REGISTER
        // -----------------------------------------------------
        const res = await fetch("/api/v1/devices/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fingerprint })
        });

        if (!res.ok) {
            throw new Error("Register request failed");
        }

        const data = await res.json();
        console.log("[BOOT] Register response:", data);

        // -----------------------------------------------------
        // REVOKED
        // -----------------------------------------------------
        if (data.state === "REVOKED") {
            showRevokedScreen();
            return;
        }

        // -----------------------------------------------------
        // STORE DEVICE ID SAFELY
        // -----------------------------------------------------
        if (data.device_id) {
            localStorage.setItem("device_id", data.device_id);
        }

        if (data.token) {
            localStorage.setItem("device_token", data.token);
        }

        // -----------------------------------------------------
        // PENDING
        // -----------------------------------------------------
        if (data.state === "PENDING") {
            showProvisioningScreen(data.device_id);
            setTimeout(() => location.reload(), 30000);
            return;
        }

        // -----------------------------------------------------
        // APPROVED / ACTIVE
        // -----------------------------------------------------
        const token = localStorage.getItem("device_token");

        if (!token) {
            throw new Error("Approved device but token missing");
        }

        // -----------------------------------------------------
        // LOAD PLAYLIST
        // -----------------------------------------------------
        const playbackRes = await fetch(
            `/api/v1/devices/${data.device_id}/playback`
        );

        if (!playbackRes.ok) {
            throw new Error("Playback fetch failed");
        }

        const playback = await playbackRes.json();
        window.__PLAYLIST__ = playback.items || [];

        console.log("[BOOT] Playlist loaded:", window.__PLAYLIST__);

        // -----------------------------------------------------
        // HIDE LOADING
        // -----------------------------------------------------
        document.getElementById("loading")?.remove();

        // -----------------------------------------------------
        // START PLAYER
        // -----------------------------------------------------
        window.startPlayer(data.device_id, token);

    } catch (err) {
        console.error("[BOOT ERROR]", err);

        document.body.innerHTML = `
            <div style="
                background:black;
                color:white;
                height:100vh;
                display:flex;
                align-items:center;
                justify-content:center;
                font-family:Arial;
            ">
                Boot error — check console
            </div>
        `;
    }
};

// -------------------------------------------------------------
// APP ENTRY
// -------------------------------------------------------------
window.addEventListener("load", () => {
    // Service worker optional (safe)
    if ("serviceWorker" in navigator) {
        navigator.serviceWorker
            .register("/service-worker.js")
            .catch(() => {});
    }

    window.bootDevice();
});
//// =============================================================