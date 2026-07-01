/**
 * 竞享成果 - 审核操作
 */

function approveOne(id) {
    confirmAction('确定要审核通过这条申报吗？', function() {
        Loading.show('正在处理...');
        fetch('/api/admin/review/' + id + '/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment: '' }),
            credentials: 'same-origin'
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            Loading.hide();
            if (d.error) {
                showToast(d.error, 'error');
            } else {
                showToast(d.message, 'success');
                setTimeout(function() { location.reload(); }, 800);
            }
        })
        .catch(function(e) {
            Loading.hide();
            showToast('操作失败: ' + e.message, 'error');
        });
    });
}

function rejectOne(id) {
    var reason = prompt('请输入驳回原因（必填）：');
    if (!reason || !reason.trim()) {
        if (reason !== null) showToast('驳回原因不能为空', 'warning');
        return;
    }
    Loading.show('正在处理...');
    fetch('/api/admin/review/' + id + '/reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: reason.trim() }),
        credentials: 'same-origin'
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        Loading.hide();
        if (d.error) {
            showToast(d.error, 'error');
        } else {
            showToast(d.message, 'success');
            setTimeout(function() { location.reload(); }, 800);
        }
    })
    .catch(function(e) {
        Loading.hide();
        showToast('操作失败: ' + e.message, 'error');
    });
}

function approveAction(id) {
    var comment = document.getElementById('review-comment').value.trim();
    Loading.show('正在处理...');
    fetch('/api/admin/review/' + id + '/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: comment }),
        credentials: 'same-origin'
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        Loading.hide();
        if (d.error) {
            showToast(d.error, 'error');
        } else {
            showToast(d.message, 'success');
            setTimeout(function() { location.reload(); }, 800);
        }
    })
    .catch(function(e) {
        Loading.hide();
        showToast('操作失败: ' + e.message, 'error');
    });
}

function rejectAction(id) {
    var comment = document.getElementById('review-comment').value.trim();
    if (!comment) {
        showToast('驳回时必须填写审核意见', 'warning');
        return;
    }
    Loading.show('正在处理...');
    fetch('/api/admin/review/' + id + '/reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: comment }),
        credentials: 'same-origin'
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        Loading.hide();
        if (d.error) {
            showToast(d.error, 'error');
        } else {
            showToast(d.message, 'success');
            setTimeout(function() { location.reload(); }, 800);
        }
    })
    .catch(function(e) {
        Loading.hide();
        showToast('操作失败: ' + e.message, 'error');
    });
}

function openImageModal(src) {
    var modal = document.getElementById('image-modal');
    var img = document.getElementById('modal-img');
    if (modal && img) {
        img.src = src;
        modal.style.display = 'flex';
    }
}
