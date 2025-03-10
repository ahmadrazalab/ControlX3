let currentPath = "";
let allFolders = [];
let allFiles = [];

async function fetchBuckets() {
  const response = await fetch("/list-buckets");
  const data = await response.json();
  const bucketSelect = document.getElementById("bucket-select");
  bucketSelect.innerHTML =
    '<option value="" disabled selected>Select a bucket</option>';

  data.buckets.forEach((bucket) => {
    const option = document.createElement("option");
    option.value = bucket;
    option.textContent = bucket;
    bucketSelect.appendChild(option);
  });
}

async function fetchRootFolders() {
  const bucket = document.getElementById("bucket-select").value;
  if (!bucket) {
    return;
  }
  const response = await fetch(`/list-files?bucket=${bucket}`);
  const data = await response.json();
  allFolders = data.folders || [];
  allFiles = data.files || [];

  updateContent(allFolders, allFiles);
  updateBreadcrumbs();
}

async function fetchFilesInFolder(path) {
  const bucket = document.getElementById("bucket-select").value;
  if (!bucket) {
    return;
  }
  const response = await fetch(
    `/list-files-in-folder?bucket=${bucket}&path=${encodeURIComponent(path)}`
  );
  const data = await response.json();
  allFolders = data.folders || [];
  allFiles = data.files || [];

  updateContent(allFolders, allFiles);
  currentPath = path;
  updateBreadcrumbs();
}

function updateContent(folders, files) {
  const content = document.getElementById("content");
  const detailsPane = document.getElementById("details-pane");

  content.innerHTML = ""; // Clear previous content
  detailsPane.classList.remove("open");

  const table = document.createElement("table");
  table.classList.add("file-table");

  table.innerHTML = `
      <thead>
        <tr>
          <th>Type</th>
          <th>Name</th>
          <th>Last Modified</th>
          <th>Preview</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
      </tbody>
    `;

  const tbody = table.querySelector("tbody");

  // Add folders to table
  folders.forEach((folder) => {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td><i class="material-icons">folder</i></td>
        <td>${folder.name}</td>
        <td>—</td>
        <td>—</td>
        <td><button onclick="fetchFilesInFolder('${folder.path}')">Open</button></td>
      `;

    tbody.appendChild(row);
  });

  // Add files to table
  files.forEach((file) => {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td><i class="material-icons">insert_drive_file</i></td>
        <td>${file.name}</td>
        <td>${file.last_modified}</td>
        <td><button onclick="previewFile('${file.path}')">Preview</button></td>
        <td><button onclick="downloadItem('${file.path}', 'file')">Download</button></td>
      `;

    tbody.appendChild(row);
  });

  content.appendChild(table);
}

function searchData() {
  const query = document.getElementById("search-input").value.toLowerCase();

  if (allFolders && allFiles) {
    const filteredFolders = allFolders.filter((folder) =>
      folder.name.toLowerCase().includes(query)
    );
    const filteredFiles = allFiles.filter((file) =>
      file.name.toLowerCase().includes(query)
    );
    updateContent(filteredFolders, filteredFiles);
  }
}

function updateBreadcrumbs() {
  const breadcrumbs = document.getElementById("breadcrumbs");
  const pathParts = currentPath.split("/").filter((part) => part.length > 0);
  breadcrumbs.innerHTML =
    '<li><a href="#" onclick="fetchRootFolders()">Home</a></li>';

  let path = "";
  pathParts.forEach((part, index) => {
    path += `/${part}`;
    breadcrumbs.innerHTML += `
              <li><a href="#" onclick="fetchFilesInFolder('${path}')">${part}</a></li>
          `;
  });
}

async function downloadItem(path, type) {
  const bucket = document.getElementById("bucket-select").value;
  if (!bucket) {
    return;
  }
  const response = await fetch(
    `/download?bucket=${bucket}&path=${encodeURIComponent(path)}&type=${type}`
  );
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download =
      type === "folder"
        ? `${path.split("/").pop()}.zip`
        : path.split("/").pop();
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } else {
    alert("Failed to download item");
  }
}

async function uploadFile() {
  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];
  const bucket = document.getElementById("bucket-select").value;

  if (!file || !bucket) {
    alert("Please select a file and bucket.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("bucket", bucket);
  formData.append("path", currentPath);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      alert("File uploaded successfully");
      fetchFilesInFolder(currentPath);
    } else {
      alert("Failed to upload file");
    }
  } catch (error) {
    alert("Error uploading file: " + error.message);
  }
}

async function previewFile(filePath) {
  const bucket = document.getElementById("bucket-select").value;
  const encodedFilename = encodeURIComponent(filePath);

  const urlResponse = await fetch(
    `/generate-url/${encodedFilename}?bucket=${bucket}`
  );
  const urlData = await urlResponse.json();

  if (urlData.url) {
    window.open(urlData.url, "_blank"); // Open preview in a new tab
  } else {
    alert("Preview not available");
  }
}

fetchBuckets();
