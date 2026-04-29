// API
// const API_BASE = "http://127.0.0.1:8000";  // for local machine only
const API_BASE = window.location.origin;

// elements
const el = {
  dropZone: document.getElementById("dropZone"),
  fileInput: document.getElementById("fileInput"),
  uploadBtn: document.getElementById("uploadBtn"),

  previewCard: document.getElementById("previewCard"),
  previewImg: document.getElementById("previewImg"),
  previewFilename: document.getElementById("previewFilename"),

  analyzeBtn: document.getElementById("analyzeBtn"),
  analyzeText: document.getElementById("analyzeBtnText"),

  resultSection: document.getElementById("resultSection"),

  errorBox: document.getElementById("errorMsg"),
  errorText: document.getElementById("errorText"),

  resetBtn: document.getElementById("resetBtn"),

  tableBody: document.getElementById("diseaseTableBody"),
  search: document.getElementById("diseaseSearch"),
  noResults: document.getElementById("noResults")
};

// state
let selectedFile = null;


// UPLOAD

el.uploadBtn.addEventListener("click", () => {
  el.fileInput.click();
});

el.fileInput.addEventListener("change", () => {
  const file = el.fileInput.files[0];
  if (file) handleFile(file);
});

el.dropZone.addEventListener("dragover", (e) => e.preventDefault());

el.dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];

  if (file && file.type.startsWith("image/")) {
    handleFile(file);
  }
});

function handleFile(file) {
  selectedFile = file;

  const reader = new FileReader();

  reader.onload = (e) => {
    el.previewImg.src = e.target.result;
    el.previewFilename.textContent = file.name;

    el.previewCard.classList.remove("hidden");
    el.dropZone.style.display = "none";

    el.analyzeBtn.disabled = false;

    hideError();
    el.resultSection.classList.remove("visible");
  };

  reader.readAsDataURL(file);
}


// RESET

el.resetBtn.addEventListener("click", () => {
  selectedFile = null;
  el.fileInput.value = "";

  el.previewCard.classList.add("hidden");
  el.dropZone.style.display = "block";

  el.analyzeBtn.disabled = true;
  el.resultSection.classList.remove("visible");

  hideError();
});


// ANALYZE

el.analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  el.analyzeBtn.disabled = true;
  el.analyzeText.textContent = "Analyzing...";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("API error");

    const data = await res.json();
    console.log("prediction:", data);

    showResult(data);

  } 
  catch (err) {
    console.error(err);
    showError("Failed to connect to API");
  }

  el.analyzeBtn.disabled = false;
  el.analyzeText.textContent = "Analyze";
});


// RESULT

function showResult(data) {
  document.getElementById("resultDiseaseName").textContent = data.disease_name;

  const percent = (data.confidence * 100).toFixed(2);

  document.getElementById("confidenceValue").textContent = percent + "%";
  document.getElementById("confidenceBar").style.width = percent + "%";

  document.getElementById("resultCause").textContent = data.cause;
  document.getElementById("resultCure").textContent = data.cure;

  el.resultSection.classList.add("visible");
}


// ERROR

function showError(msg) {
  el.errorText.textContent = msg;
  el.errorBox.classList.add("visible");
}

function hideError() {
  el.errorBox.classList.remove("visible");
}

// DISEASE CLASS
const DISEASE_CLASSES=[
{crop:'Apple',disease:'Apple Scab',healthy:false},
{crop:'Apple',disease:'Black Rot',healthy:false},
{crop:'Apple',disease:'Cedar Apple Rust',healthy:false},
{crop:'Apple',disease:'Healthy',healthy:true},
{crop:'Blueberry',disease:'Healthy',healthy:true},
{crop:'Cherry',disease:'Powdery Mildew',healthy:false},
{crop:'Cherry',disease:'Healthy',healthy:true},
{crop:'Corn',disease:'Cercospora Leaf Spot / Gray Leaf Spot',healthy:false},
{crop:'Corn',disease:'Common Rust',healthy:false},
{crop:'Corn',disease:'Northern Leaf Blight',healthy:false},
{crop:'Corn',disease:'Healthy',healthy:true},
{crop:'Grape',disease:'Black Rot',healthy:false},
{crop:'Grape',disease:'Esca (Black Measles)',healthy:false},
{crop:'Grape',disease:'Leaf Blight (Isariopsis Leaf Spot)',healthy:false},
{crop:'Grape',disease:'Healthy',healthy:true},
{crop:'Orange',disease:'Huanglongbing (Citrus Greening)',healthy:false},
{crop:'Peach',disease:'Bacterial Spot',healthy:false},
{crop:'Peach',disease:'Healthy',healthy:true},
{crop:'Pepper',disease:'Bacterial Spot',healthy:false},
{crop:'Pepper',disease:'Healthy',healthy:true},
{crop:'Potato',disease:'Early Blight',healthy:false},
{crop:'Potato',disease:'Late Blight',healthy:false},
{crop:'Potato',disease:'Healthy',healthy:true},
{crop:'Raspberry',disease:'Healthy',healthy:true},
{crop:'Soybean',disease:'Healthy',healthy:true},
{crop:'Squash',disease:'Powdery Mildew',healthy:false},
{crop:'Strawberry',disease:'Leaf Scorch',healthy:false},
{crop:'Strawberry',disease:'Healthy',healthy:true},
{crop:'Tomato',disease:'Bacterial Spot',healthy:false},
{crop:'Tomato',disease:'Early Blight',healthy:false},
{crop:'Tomato',disease:'Late Blight',healthy:false},
{crop:'Tomato',disease:'Leaf Mold',healthy:false},
{crop:'Tomato',disease:'Septoria Leaf Spot',healthy:false},
{crop:'Tomato',disease:'Spider Mites (Two-Spotted Spider Mite)',healthy:false},
{crop:'Tomato',disease:'Target Spot',healthy:false},
{crop:'Tomato',disease:'Yellow Leaf Curl Virus',healthy:false},
{crop:'Tomato',disease:'Mosaic Virus',healthy:false},
{crop:'Tomato',disease:'Healthy',healthy:true}
];
// TABLE

function renderTable(filter = "") {
  const q = filter.toLowerCase();

  const list = DISEASE_CLASSES
    .filter(d =>
      d.crop.toLowerCase().includes(q) ||
      d.disease.toLowerCase().includes(q)
    )
    .sort((a, b) => a.healthy - b.healthy);

  el.tableBody.innerHTML = list.map((d, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${d.crop}</td>
      <td>${d.disease}</td>
      <td>
        <span class="status-tag ${d.healthy ? "healthy" : "diseased"}">
          ${d.healthy ? "Healthy" : "Diseased"}
        </span>
      </td>
    </tr>
  `).join("");

  el.noResults.style.display = list.length ? "none" : "block";
}


// init
renderTable();

// search
el.search.addEventListener("input", (e) => {
  renderTable(e.target.value);
});