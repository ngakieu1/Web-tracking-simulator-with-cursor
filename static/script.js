
let tracking = false;
let startTime = null;
let intervalID = null;
let mouseData = [];

document.getElementById("startBtn").onclick = () => {
    tracking = true;
    startTime = Date.now();
    // intervalID = setInterval(sendMousePosition, 100);
    mouseData = [];
};

document.getElementById("stopBtn").onclick = () => {
    tracking = false;
    clearInterval(intervalID);

    fetch('/save_and_analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mouseData)
        // send the tracked mouse data here
    })
    .then(res => res.json())
    .then(data => {
        if (data.stats) renderStats(data.stats);
        if (data.transitions) renderTransitions(data.transitions);

        if (data.success){
            const output = document.getElementById("output");
            output.innerHTML = `CSV saved: <a href="${data.csv}" target="_blank">${data.csv}</a>`;
            // window.location.href = "/results";
        }
    })
    .catch(err => console.error(err));
};

function renderStats(stats) {
    const tbody = document.getElementById("statsTable").querySelector("tbody");
    tbody.innerHTML = "";
    for (const [aoi, values] of Object.entries(stats)) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${aoi}</td>
            <td>${values.Mean.toFixed(3)}</td>
            <td>${values.SD.toFixed(3)}</td>
            <td>${values.Min.toFixed(3)}</td>
            <td>${values.Max.toFixed(3)}</td>
        `;
        tbody.appendChild(row);
    }
}

document.addEventListener("mousemove", (e) => {
    if (!tracking) return;

    const img = document.querySelector(".background-image");
    const imgRect = img.getBoundingClientRect();
    const timestamp = ((Date.now() - startTime)/1000).toFixed(3);
    mouseData.push({
        timestamp,
        // x: e.clientX,
        // y: e.clientY,
        // screen_width: window.innerWidth,
        // screen_height: window.innerHeight
        x: e.clientX - imgRect.left,
        y: e.clientY - imgRect.top,
        // timestamp: performance.now(),
        image_width: img.width,
        image_height: img.height,
    });
});

function renderTransitions(transitions) {
    const tbody = document.getElementById("transitionsTable").querySelector("tbody");
    tbody.innerHTML = "";
    for (const [trans, prob] of Object.entries(transitions)) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${trans}</td>
            <td>${(prob * 100).toFixed(1)}%</td>
        `;
        tbody.appendChild(row);
    }
}


