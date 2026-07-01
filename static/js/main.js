/**
 * 竞享成果——学生竞赛获奖申报平台
 * Shared JavaScript utilities
 */

// Show/hide loading overlay
const Loading = {
    show: function(text) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.querySelector('.loading-text').textContent = text || '加载中...';
            overlay.style.display = 'flex';
        }
    },
    hide: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';
    }
};

// Toast notification (in-page, non-flask)
function showToast(message, type) {
    type = type || 'info';
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const container = document.getElementById('toast-container');
    if (!container) {
        // Fallback: create container
        const div = document.createElement('div');
        div.id = 'toast-container';
        div.style.cssText = 'position:fixed;top:58px;left:50%;transform:translateX(-50%);z-index:2000;display:flex;flex-direction:column;gap:8px;width:calc(100%-32px);max-width:420px;pointer-events:none;';
        document.body.appendChild(div);
        return showToast(message, type);
    }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML = '<span class="toast-icon">' + icons[type] + '</span><span class="toast-message">' + message + '</span>';
    toast.onclick = function() { toast.remove(); };
    container.appendChild(toast);
    setTimeout(function() {
        if (toast.parentNode) toast.remove();
    }, 4000);
}

// Auto-hide flash toasts after 4 seconds
document.addEventListener('DOMContentLoaded', function() {
    var toasts = document.querySelectorAll('.toast');
    toasts.forEach(function(t) {
        setTimeout(function() { t.remove(); }, 4000);
    });
});

// Form validation helper
function validateForm(form, rules) {
    var valid = true;
    for (var field in rules) {
        var rule = rules[field];
        var el = form.querySelector('[name="' + field + '"]');
        var group = el ? el.closest('.form-group') : null;
        var errorEl = group ? group.querySelector('.form-error') : null;

        if (!el) continue;
        var value = el.value.trim();

        // Required check
        if (rule.required && !value) {
            showFieldError(group, errorEl, rule.requiredMsg || '此字段为必填项');
            valid = false;
            continue;
        }

        // Min length
        if (rule.minLength && value.length < rule.minLength) {
            showFieldError(group, errorEl, rule.minLengthMsg || ('至少需要 ' + rule.minLength + ' 个字符'));
            valid = false;
            continue;
        }

        // Pattern
        if (rule.pattern && !rule.pattern.test(value)) {
            showFieldError(group, errorEl, rule.patternMsg || '格式不正确');
            valid = false;
            continue;
        }

        clearFieldError(group, errorEl);
    }
    return valid;
}

function showFieldError(group, errorEl, msg) {
    if (group) group.classList.add('error');
    if (errorEl) errorEl.textContent = msg;
}

function clearFieldError(group, errorEl) {
    if (group) group.classList.remove('error');
    if (errorEl) errorEl.textContent = '';
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// API helper
function api(url, options) {
    options = options || {};
    options.credentials = 'same-origin';
    if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
        options.headers = options.headers || {};
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    return fetch(url, options).then(function(res) {
        return res.json().then(function(data) {
            if (!res.ok) {
                throw new Error(data.error || '请求失败');
            }
            return data;
        });
    });
}
