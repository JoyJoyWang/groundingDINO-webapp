// No need to store original image previews anymore

async function uploadImages() {
  const files = document.getElementById('fileInput').files;
  if (files.length === 0) return;

  document.getElementById('status').textContent = 'Processing...';
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file);
  }
  // Add thresholds and prompt
  formData.append('box_threshold', document.getElementById('boxThresholdInput').value);
  formData.append('text_threshold', document.getElementById('textThresholdInput').value);
  formData.append('prompt', document.getElementById('promptInput').value);

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
  const processedImageUrls = [];

  // Only show processed images, make them responsive, and clickable for pop-up
  for (let i = 0; i < data.results.length; i++) {
    const result = data.results[i];
    // Container for processed image and download link
    const container = document.createElement('div');
    container.className = 'flex flex-col items-center border p-2 rounded';

    // Processed image (from server)
    const procImgElem = document.createElement('img');
    procImgElem.src = '/static/' + result.output;
    procImgElem.className = 'border';
    procImgElem.title = 'Processed';
    procImgElem.style.maxWidth = '100%';
    procImgElem.style.height = 'auto';
    procImgElem.style.display = 'block';
    procImgElem.style.margin = '0 auto';
    procImgElem.style.maxHeight = '70vh';
    procImgElem.style.cursor = 'pointer';
    procImgElem.onclick = function() {
      showProcessedModal(procImgElem.src);
    };

    // Download link for processed image
    const downloadLink = document.createElement('a');
    downloadLink.href = procImgElem.src;
    downloadLink.download = result.output;
    downloadLink.textContent = 'Download Processed';
    downloadLink.className = 'text-blue-600 underline mt-2';

    processedImageUrls.push(procImgElem.src);

    // Add to container
    container.appendChild(procImgElem);
    container.appendChild(downloadLink);
    resultDiv.appendChild(container);
  }

  // Show Download All button if there are processed images
  const downloadAllBtn = document.getElementById('downloadAllBtn');
  if (processedImageUrls.length > 0) {
    downloadAllBtn.classList.remove('hidden');
    downloadAllBtn.processedImageUrls = processedImageUrls;
  } else {
    downloadAllBtn.classList.add('hidden');
  }

  document.getElementById('status').textContent = 'Done.';
}

// Download all processed images (one by one)
function downloadAllImages() {
  const btn = document.getElementById('downloadAllBtn');
  const urls = btn.processedImageUrls || [];
  for (const url of urls) {
    const a = document.createElement('a');
    a.href = url;
    a.download = url.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

// Show processed image in a modal pop-up
function showProcessedModal(imgUrl) {
  let modal = document.getElementById('processedModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'processedModal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(0,0,0,0.7)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '1000';
    modal.onclick = function() { modal.style.display = 'none'; };
    const img = document.createElement('img');
    img.id = 'processedModalImg';
    img.style.maxWidth = '90vw';
    img.style.maxHeight = '90vh';
    img.style.boxShadow = '0 0 20px #000';
    modal.appendChild(img);
    document.body.appendChild(modal);
  }
  const img = document.getElementById('processedModalImg');
  img.src = imgUrl;
  modal.style.display = 'flex';
}