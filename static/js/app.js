/* filepath: /Users/v01d/Developer/GameDevAssetCatalogue/GameDevAssetCatalogue/static/js/app.js */

let token = localStorage.getItem('token');
let currentUsername = '';

// Auth Functions
function handleEnter(event) {
    if (event.key === 'Enter') {
        login();
    }
}

async function register() {
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    
    if (!username || !password) {
        document.getElementById('authStatus').innerText = 'Please enter username and password';
        return;
    }
    
    const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    
    if (response.ok) {
        document.getElementById('authStatus').style.color = 'green';
        document.getElementById('authStatus').innerText = 'Registration successful! Please login.';
        document.getElementById('authPassword').value = '';
    } else {
        const error = await response.json();
        document.getElementById('authStatus').style.color = 'red';
        document.getElementById('authStatus').innerText = error.detail || 'Registration failed';
    }
}

async function login() {
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    
    if (!username || !password) {
        document.getElementById('authStatus').innerText = 'Please enter username and password';
        return;
    }
    
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    
    if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        currentUsername = username;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        showMainApp();
    } else {
        document.getElementById('authStatus').style.color = 'red';
        document.getElementById('authStatus').innerText = 'Invalid credentials';
    }
}

function logout() {
    token = null;
    currentUsername = '';
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
    document.getElementById('authStatus').innerText = '';
}

function showMainApp() {
    currentUsername = localStorage.getItem('username') || 'User';
    document.getElementById('currentUsername').querySelector('strong').innerText = currentUsername;
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    loadAssets();
}

// Form Functions
function toggleForm() {
    const form = document.getElementById('assetForm');
    form.classList.toggle('show');
    if (!form.classList.contains('show')) {
        resetForm();
    }
}

function resetForm() {
    document.getElementById('assetForm').reset();
    document.getElementById('assetForm').dataset.assetId = '';
    document.getElementById('assetForm').querySelector('h2').innerText = 'Create New Asset';
    document.getElementById('assetForm').querySelector('button[type="button"]:first-of-type').innerText = 'Create Asset';
}

// Asset Functions
async function loadAssets(category = '', tags = '') {
    let url = '/api/assets';
    const params = new URLSearchParams();
    
    if (category) params.append('category', category);
    if (tags) params.append('tags', tags);
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    try {
        const response = await fetch(url, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        if (!response.ok) {
            console.log('Failed to load assets, status:', response.status);
            if (response.status === 401 || response.status === 403) {
                logout();
            }
            return;
        }
        
        const data = await response.json();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        
        data.assets.forEach(asset => {
            // Generate thumbnail if file exists and is an image
            let fileDisplay = 'None';
            if (asset.file_path) {
                const ext = asset.file_path.toLowerCase().split('.').pop();
                const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
                
                if (imageExts.includes(ext)) {
                    fileDisplay = `
                        <div class="file-cell">
                            <img src="/api/assets/${asset.id}/file-preview" class="file-thumbnail" onerror="this.style.display='none'">
                            <a href="#" onclick="downloadFile(${asset.id}); return false;">Download</a>
                        </div>
                    `;
                } else {
                    fileDisplay = `<a href="#" onclick="downloadFile(${asset.id}); return false;">Download</a>`;
                }
            }
            
            // Main asset row
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${asset.id}</td>
                <td>${asset.name}</td>
                <td>${asset.category}</td>
                <td>${asset.license_type}</td>
                <td>${asset.tags.join(', ')}</td>
                <td><a href="${asset.source_url}" target="_blank">Link</a></td>
                <td>${fileDisplay}</td>
                <td>
                    <button onclick="editAsset(${asset.id})">Edit</button>
                    <button onclick="deleteAsset(${asset.id})">Delete</button>
                </td>
            `;
            
            // Description row
            const descRow = tbody.insertRow();
            descRow.innerHTML = `
                <td colspan="8" class="description-row">
                    <strong>Description:</strong> ${asset.description || 'No description provided'}
                </td>
            `;
        });
    } catch (err) {
        console.error('Error loading assets:', err);
        alert('Error loading assets');
    }
}

async function editAsset(asset_id) {
    const response = await fetch(`/api/assets/${asset_id}`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    const asset = await response.json();
    
    const tagsString = Array.isArray(asset.tags) ? asset.tags.join(', ') : asset.tags;
    
    document.getElementById('name').value = asset.name;
    document.getElementById('category').value = asset.category;
    document.getElementById('license_type').value = asset.license_type;
    document.getElementById('source_url').value = asset.source_url;
    document.getElementById('description').value = asset.description || '';
    document.getElementById('tags').value = tagsString;
    
    document.getElementById('assetForm').querySelector('h2').innerText = 'Edit Asset';
    document.getElementById('assetForm').querySelector('button[type="button"]:first-of-type').innerText = 'Update Asset';
    document.getElementById('assetForm').dataset.assetId = asset_id;
    
    document.getElementById('assetForm').classList.add('show');
    document.getElementById('assetForm').scrollIntoView({ behavior: 'smooth' });
}

async function submitForm() {
    const assetId = document.getElementById('assetForm').dataset.assetId;
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('category', document.getElementById('category').value);
    formData.append('license_type', document.getElementById('license_type').value);
    formData.append('source_url', document.getElementById('source_url').value);
    
    const description = document.getElementById('description').value;
    if (description) {
        formData.append('description', description);
    }
    
    const tags = document.getElementById('tags').value;
    if (tags) {
        formData.append('tags', tags);
    }
    
    const file = document.getElementById('file').files[0];
    if (file) {
        formData.append('file', file);
    }

    let url = '/api/assets';
    let method = 'POST';
    
    if (assetId) {
        url = `/api/assets/${assetId}`;
        method = 'PUT';
    }

    const response = await fetch(url, {
        method: method,
        headers: {'Authorization': `Bearer ${token}`},
        body: formData
    });

    if (response.ok) {
        resetForm();
        toggleForm();
        clearFilters();
    } else {
        const error = await response.json();
        alert('Error: ' + JSON.stringify(error));
    }
}

async function deleteAsset(asset_id) {
    if (confirm('Are you sure you want to delete this asset?')) {
        const response = await fetch(`/api/assets/${asset_id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${token}`}
        });

        if (response.ok) {
            applyFilters();
        } else {
            alert('Error deleting asset');
        }
    }
}

async function downloadFile(asset_id) {
    try {
        const response = await fetch(`/api/assets/${asset_id}/file`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        if (!response.ok) {
            alert('Error downloading file');
            return;
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'asset_file';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (err) {
        console.error('Error downloading file:', err);
        alert('Error downloading file');
    }
}

// Filter Functions
function applyFilters() {
    const category = document.getElementById('filterCategory').value;
    const tags = document.getElementById('filterTags').value;
    loadAssets(category, tags);
}

function clearFilters() {
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterTags').value = '';
    loadAssets();
}

// Initialize on page load
if (token) {
    fetch('/api/assets', {
        headers: {'Authorization': `Bearer ${token}`}
    }).then(response => {
        if (response.ok) {
            showMainApp();
        } else {
            console.log('Token invalid, logging out');
            localStorage.removeItem('token');
            token = null;
        }
    }).catch(err => {
        console.log('Error validating token:', err);
        localStorage.removeItem('token');
        token = null;
    });
}