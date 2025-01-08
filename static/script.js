document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('stlFile');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/estimate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        resultDiv.classList.remove('d-none');
        resultContent.textContent = JSON.stringify(data, null, 2);
        
        if (!response.ok) {
            throw new Error(data.error || 'Unknown error occurred');
        }
    } catch (error) {
        resultDiv.classList.remove('d-none');
        resultContent.textContent = JSON.stringify({error: error.message}, null, 2);
    }
});
