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
function previewImage(input) {
    var file = input.files[0];
    if (!file) return;

    // Validate file type
    var validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (validTypes.indexOf(file.type) === -1 && !file.name.match(/\.(jpg|jpeg|png|pdf)$/i)) {
        showToast('不支持的文件格式，请上传 JPG、PNG 或 PDF', 'error');
        input.value = '';
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('文件大小不能超过 10MB', 'error');
        input.value = '';
        return;
    }

    // PDF preview
    if (file.type === 'application/pdf' || file.name.match(/\.pdf$/i)) {
        document.getElementById('upload-icon').textContent = '📄';
        document.getElementById('upload-text').textContent = '已选择: ' + file.name;
        document.getElementById('preview-container').style.display = 'none';
        return;
    }

    // Image preview
    var reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('preview-img').src = e.target.result;
        document.getElementById('preview-container').style.display = 'inline-block';
        document.getElementById('upload-icon').textContent = '✅';
        document.getElementById('upload-text').textContent = '点击重新选择';
    };
    reader.readAsDataURL(file);
}

// Remove preview
function removePreview() {
    document.getElementById('certificate').value = '';
    document.getElementById('preview-container').style.display = 'none';
    document.getElementById('preview-img').src = '';
    document.getElementById('upload-icon').textContent = '📷';
    document.getElementById('upload-text').textContent = '点击上传获奖证书图片';
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
