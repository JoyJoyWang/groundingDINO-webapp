async function uploadImages() {
  const files = document.getElementById('fileInput').files;
  if (files.length === 0) return;

  document.getElementById('status').textContent = 'Processing...';
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file);
  }

  const response = await fetch('/upload', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  console.log("response data:", data); 
  console.log("data.results type:", typeof data.results, Array.isArray(data.results));

  
  if (data.error) {
    document.getElementById('status').textContent = "Error: " + data.error;
    alert("Upload failed: " + data.error);
    return;
  }
  
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '';
  for (const img of data.results) {
    const imgElem = document.createElement('img');
    imgElem.src = '/static/' + img;
    imgElem.className = 'w-full border';
    resultDiv.appendChild(imgElem);
  }
  

  document.getElementById('status').textContent = 'Done.';
}