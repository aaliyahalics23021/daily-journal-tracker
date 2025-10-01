async function saveEntry() {
  let title = document.getElementById("title").value;
  let content = document.getElementById("content").value;

  if (!title || !content) {
    alert("Please enter title and content!");
    return;
  }

  let res = await fetch("http://127.0.0.1:5000/api/entry", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content })
  });

  let data = await res.json();
  alert(data.commit);
  document.getElementById("title").value = "";
  document.getElementById("content").value = "";
  loadEntries();
}

async function loadEntries() {
  let res = await fetch("http://127.0.0.1:5000/api/entries");
  let data = await res.json();

  let container = document.getElementById("entries");
  container.innerHTML = "";
  data.forEach(e => {
    let div = document.createElement("div");
    div.className = "entry";
    div.innerHTML = `
      <b>${e.filename}</b><br>
      ${e.preview}<br>
      <button onclick="deleteEntry('${e.filename}')">🗑️ Delete</button>
    `;
    container.appendChild(div);
  });
}

async function deleteEntry(filename) {
  if (!confirm(`Delete ${filename}?`)) return;
  let res = await fetch(`http://127.0.0.1:5000/api/entry/${filename}`, {
    method: "DELETE"
  });
  let data = await res.json();
  alert(data.message || data.error);
  loadEntries();
}

window.onload = loadEntries;
