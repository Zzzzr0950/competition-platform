/**
 * 竞享成果 - 申报表单交互逻辑
 */

// Accordion toggle
function toggleAccordion(header) {
    var group = header.parentElement;
    var body = group.querySelector('.accordion-body');
    if (group.classList.contains('open')) {
        group.classList.remove('open');
        body.style.display = 'none';
    } else {
        group.classList.add('open');
        body.style.display = 'block';
    }
}

// Select a competition
function selectCompetition(item) {
    // Remove all selected states
    document.querySelectorAll('.accordion-item').forEach(function(el) {
        el.classList.remove('selected');
    });
    // Set selected
    item.classList.add('selected');
    // Update hidden input
    document.getElementById('catalog_id').value = item.dataset.id;
    // Update search box
    var searchBox = document.getElementById('catalog-search');
    searchBox.value = item.dataset.name;
    searchBox.style.color = '#1f2937';
    searchBox.style.fontWeight = '600';
    // Clear error
    document.getElementById('group-catalog').classList.remove('error');
}

// Filter accordion items
function filterCatalogAccordion() {
    var search = document.getElementById('catalog-search').value.toLowerCase();
    var groups = document.querySelectorAll('.accordion-group');

    groups.forEach(function(group) {
        var items = group.querySelectorAll('.accordion-item');
        var hasVisible = false;

        items.forEach(function(item) {
            var name = (item.dataset.name || '').toLowerCase();
            if (name.indexOf(search) >= 0) {
                item.classList.remove('hidden-by-search');
                hasVisible = true;
            } else {
                item.classList.add('hidden-by-search');
            }
        });

        // Auto-expand group if it has matching items and user is searching
        if (search && hasVisible) {
            group.classList.add('open');
            group.querySelector('.accordion-body').style.display = 'block';
        } else if (!search) {
            // When search is cleared, collapse all
            group.classList.remove('open');
            group.querySelector('.accordion-body').style.display = 'none';
        }
    });

    // If user is modifying the search box text, clear selection
    var selected = document.querySelector('.accordion-item.selected');
    var searchBox = document.getElementById('catalog-search');
    if (selected && searchBox.value !== selected.dataset.name) {
        selected.classList.remove('selected');
        document.getElementById('catalog_id').value = '';
        searchBox.style.color = '';
        searchBox.style.fontWeight = '';
    }
}

// Image preview
function previewImages(input) {
    var files = input.files;
    if (!files || files.length === 0) return;
    var list = document.getElementById('preview-list');
    list.innerHTML = '';

    document.getElementById('upload-icon').textContent = files.length > 1 ? '📑' : '📷';
    document.getElementById('upload-text').textContent = '已选 ' + files.length + ' 个文件';

    for (var i = 0; i < files.length; i++) {
        (function(file, idx) {
            if (file.type === 'application/pdf' || file.name.match(/\.pdf$/i)) {
                var div = document.createElement('div');
                div.style.cssText = 'width:80px;height:60px;border-radius:6px;border:1px solid #e5e7eb;display:flex;align-items:center;justify-content:center;font-size:0.7rem;background:#fef2f2;color:#dc2626;position:relative;';
                div.innerHTML = '<span>PDF</span><button onclick="removeOne('+idx+')" style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#dc2626;color:#fff;border:none;border-radius:50%;font-size:0.7rem;cursor:pointer;">✕</button>';
                list.appendChild(div);
            } else {
                var div = document.createElement('div');
                div.style.cssText = 'width:80px;height:60px;border-radius:6px;overflow:hidden;border:1px solid #e5e7eb;position:relative;';
                var img = document.createElement('img');
                img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
                div.appendChild(img);
                var btn = document.createElement('button');
                btn.style.cssText = 'position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#dc2626;color:#fff;border:none;border-radius:50%;font-size:0.7rem;cursor:pointer;';
                btn.textContent = '✕';
                btn.onclick = function() { removeOne(idx); };
                div.appendChild(btn);
                list.appendChild(div);
                var reader = new FileReader();
                reader.onload = function(e) { img.src = e.target.result; };
                reader.readAsDataURL(file);
            }
        })(files[i], i);
    }
}

function removeOne(idx) {
    document.getElementById('certificate').value = '';
    document.getElementById('preview-list').innerHTML = '';
    document.getElementById('upload-icon').textContent = '📷';
    document.getElementById('upload-text').textContent = '点击上传获奖证书图片（可多选）';
}

// Drag and drop support
(function() {
    var zone = document.getElementById('upload-zone');
    if (!zone) return;

    zone.addEventListener('dragover', function(e) {
        e.preventDefault();
        zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', function(e) {
        e.preventDefault();
        zone.classList.remove('drag-over');
        var files = e.dataTransfer.files;
        if (files.length > 0) {
            var input = document.getElementById('certificate');
            input.files = files;
            previewImage(input);
        }
    });
})();

// Form submission
document.getElementById('submit-form').addEventListener('submit', function(e) {
    e.preventDefault();

    // Client-side validation
    var catalogId = document.getElementById('catalog_id').value;
    var awardLevel = document.getElementById('award_level').value;
    var awardTier = document.getElementById('award_tier').value;
    var awardDate = document.getElementById('award_date').value;

    var valid = true;

    if (!catalogId) {
        document.getElementById('group-catalog').classList.add('error');
        valid = false;
    } else {
        document.getElementById('group-catalog').classList.remove('error');
    }

    if (!awardLevel.trim()) {
        document.getElementById('group-award_level').classList.add('error');
        valid = false;
    } else {
        document.getElementById('group-award_level').classList.remove('error');
    }

    if (!awardTier) {
        document.getElementById('group-award_tier').classList.add('error');
        valid = false;
    } else {
        document.getElementById('group-award_tier').classList.remove('error');
    }

    if (!awardDate) {
        document.getElementById('group-award_date').classList.add('error');
        valid = false;
    } else {
        document.getElementById('group-award_date').classList.remove('error');
    }

    if (!valid) {
        showToast('请填写所有必填项', 'warning');
        return;
    }

    // Build form data
    var formData = new FormData();
    formData.append('catalog_id', catalogId);
    formData.append('award_level', awardLevel);
    formData.append('award_tier', awardTier);
    formData.append('award_date', awardDate);
    formData.append('team_name', document.getElementById('team_name').value);
    formData.append('team_members', document.getElementById('team_members').value);
    formData.append('is_leader', document.getElementById('is_leader').checked ? '1' : '0');

    var fileInput = document.getElementById('certificate');
    if (fileInput.files.length > 0) {
        formData.append('certificate', fileInput.files[0]);
    }

    var btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.textContent = '提交中...';
    Loading.show('正在提交申报...');

    fetch('/api/submissions', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        Loading.hide();
        if (data.error) {
            showToast(data.error, 'error');
            btn.disabled = false;
            btn.textContent = '提 交 申 报';
        } else {
            showToast(data.message, 'success');
            setTimeout(function() {
                window.location.href = '/my-submissions';
            }, 1500);
        }
    })
    .catch(function(err) {
        Loading.hide();
        showToast('网络错误: ' + err.message, 'error');
        btn.disabled = false;
        btn.textContent = '提 交 申 报';
    });
});
