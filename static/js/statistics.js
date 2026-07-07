/**
 * 竞享成果 - 统计图表 (原生 Canvas 实现)
 */

document.addEventListener('DOMContentLoaded', function() {
    loadOverview();
    loadByLevel();
    loadByCompetition();
    loadByClass();
    loadClassOptions();
});

/** 填充导出班级下拉框 */
function loadClassOptions() {
    var select = document.getElementById('export-class');
    if (!select) return;
    fetchJSON('/api/admin/statistics/by-class')
        .then(function(data) {
            data.forEach(function(d) {
                var opt = document.createElement('option');
                opt.value = d.class_name;
                opt.textContent = d.class_name + ' (' + d.count + '条)';
                select.appendChild(opt);
            });
        })
        .catch(function(err) {
            console.error('加载班级列表失败:', err.message);
        });
}

/** 执行导出 */
function doExport() {
    var className = document.getElementById('export-class').value;
    var url = '/api/admin/export';
    if (className) {
        url += '?class_name=' + encodeURIComponent(className);
    }
    window.location.href = url;
}

/**
 * 通用 fetch 封装：处理 302 重定向、非 JSON 响应等异常情况
 */
function fetchJSON(url) {
    return fetch(url, { credentials: 'same-origin' })
        .then(function(res) {
            // 如果被重定向到登录页，说明 session 过期
            if (res.redirected || res.status === 302 || res.status === 401) {
                throw new Error('SESSION_EXPIRED');
            }
            if (!res.ok) {
                throw new Error('HTTP ' + res.status + ' ' + res.statusText);
            }
            // 检查 Content-Type 是否为 JSON
            var contentType = res.headers.get('Content-Type') || '';
            if (contentType.indexOf('application/json') === -1) {
                // 可能是 HTML 登录页（session 过期等）
                throw new Error('INVALID_RESPONSE');
            }
            return res.json();
        });
}

/**
 * 在容器中显示错误信息
 */
function showChartError(containerId, message) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div style="text-align:center;padding:40px 20px;color:#dc2626;font-size:0.9rem;">'
        + '<div style="font-size:2rem;margin-bottom:8px;">⚠</div>'
        + '<div>' + message + '</div>'
        + '</div>';
}

function loadOverview() {
    fetchJSON('/api/admin/statistics/overview')
        .then(function(d) {
            document.getElementById('stat-total').textContent = d.total;
            document.getElementById('stat-pending').textContent = d.pending;
            document.getElementById('stat-approved').textContent = d.approved;
            document.getElementById('stat-students').textContent = d.student_count;
        })
        .catch(function(err) {
            console.error('统计概览加载失败:', err.message);
            document.getElementById('stat-total').textContent = '!';
            document.getElementById('stat-pending').textContent = '!';
            document.getElementById('stat-approved').textContent = '!';
            document.getElementById('stat-students').textContent = '!';
        });
}

function loadByLevel() {
    fetchJSON('/api/admin/statistics/by-level')
        .then(function(data) {
            drawBarChart('chart-level', data, 'level', 'count',
                { '国家级': '#6d28d9', '省级': '#1d4ed8', '校级': '#4b5563' });
        })
        .catch(function(err) {
            console.error('按级别统计加载失败:', err.message);
            showChartError('chart-level', '数据加载失败，请刷新页面重试');
        });
}

/** 清理竞赛名称：去掉 ①②③... 及其后面的子项目 */
function cleanCompetitionName(name) {
    // 找到第一个圈圈数字的位置
    var circled = name.search(/[①-⑳]/);  // ①-⑳
    if (circled === -1) return name;
    // 往前找分隔符，从分隔符开始裁掉
    var before = name.slice(0, circled);
    var sep = before.search(/[—\-：:，,、\s]+$/);
    if (sep !== -1) return before.slice(0, sep);
    return before;
}

function loadByCompetition() {
    fetchJSON('/api/admin/statistics/by-competition?limit=10')
        .then(function(data) {
            var labels = data.map(function(d) { return cleanCompetitionName(d.name); });
            var values = data.map(function(d) { return d.count; });
            drawHorizontalBarChart('chart-competition', labels, values);
        })
        .catch(function(err) {
            console.error('按竞赛统计加载失败:', err.message);
            showChartError('chart-competition', '数据加载失败，请刷新页面重试');
        });
}

function loadByClass() {
    fetchJSON('/api/admin/statistics/by-class')
        .then(function(data) {
            drawBarChart('chart-class', data, 'class_name', 'count', {});
        })
        .catch(function(err) {
            console.error('按班级统计加载失败:', err.message);
            showChartError('chart-class', '数据加载失败，请刷新页面重试');
        });
}

/**
 * Vertical bar chart — used by "按竞赛级别" and "按班级"
 * Labels are horizontal, font auto-shrinks to fit bar width
 */
function drawBarChart(containerId, data, labelKey, valueKey, colorMap) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 350;
    canvas.height = 300;
    canvas.style.width = '100%';
    canvas.style.height = '300px';
    container.innerHTML = '';
    container.appendChild(canvas);

    if (!data || data.length === 0) {
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#9ca3af';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('暂无数据', canvas.width / 2, canvas.height / 2);
        return;
    }

    var ctx = canvas.getContext('2d');
    if (!ctx) { container.innerHTML = '<div style="text-align:center;padding:20px;color:#9ca3af;">浏览器不支持 Canvas</div>'; return; }

    var padding = { top: 20, right: 20, bottom: 50, left: 50 };
    var chartW = canvas.width - padding.left - padding.right;
    var chartH = canvas.height - padding.top - padding.bottom;

    var maxVal = Math.max.apply(null, data.map(function(d) { return d[valueKey]; }));
    maxVal = Math.ceil(maxVal * 1.2 / 5) * 5 || 10;
    var barWidth = Math.min(60, chartW / data.length * 0.7);
    var gap = (chartW - barWidth * data.length) / (data.length + 1);

    // Auto-fit label font: smaller for more bars, but at least 9px
    var labelFontSize = Math.max(9, Math.min(11, barWidth * 0.85 / (data[0] ? (data[0][labelKey] || '').length : 1)));

    // Grid lines
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    for (var i = 0; i <= 4; i++) {
        var y = padding.top + chartH * i / 4;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(canvas.width - padding.right, y);
        ctx.stroke();
        ctx.fillStyle = '#6b7280';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round(maxVal - maxVal * i / 4), padding.left - 8, y + 4);
    }

    // Bars
    data.forEach(function(d, i) {
        var x = padding.left + gap + i * (barWidth + gap);
        var barH = (d[valueKey] / maxVal) * chartH;
        var barY = padding.top + chartH - barH;

        var defaultColors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                             '#f59e0b', '#f97316', '#ef4444', '#8b5cf6', '#10b981'];
        var color = colorMap[d[labelKey]] || defaultColors[i % defaultColors.length];

        ctx.fillStyle = color;
        ctx.fillRect(x, barY, barWidth, barH);

        // Value on top
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(d[valueKey], x + barWidth / 2, barY - 6);

        // Label below — 水平居中，缩小字号，完整显示
        ctx.fillStyle = '#4b5563';
        ctx.font = labelFontSize + 'px sans-serif';
        ctx.textAlign = 'center';
        var labelText = d[labelKey] || '';
        ctx.fillText(labelText, x + barWidth / 2, padding.top + chartH + 18);
    });
}

/**
 * Horizontal bar chart for competition names
 * All bars same width, labels dynamically sized to fit
 */
function drawHorizontalBarChart(containerId, labels, values) {
    var container = document.getElementById(containerId);
    if (!container) return;

    container.style.overflowX = 'auto';

    // Use a generous canvas width
    var canvasW = Math.max(container.clientWidth || 350, 600);
    var canvas = document.createElement('canvas');
    canvas.width = canvasW;
    canvas.style.display = 'block';
    var ctx = canvas.getContext('2d');
    if (!ctx) { container.innerHTML = '<div style="text-align:center;padding:20px;color:#9ca3af;">浏览器不支持 Canvas</div>'; return; }

    if (!labels || labels.length === 0) {
        canvas.height = 220;
        ctx.fillStyle = '#9ca3af';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('暂无数据', canvas.width / 2, canvas.height / 2);
        container.innerHTML = '';
        container.appendChild(canvas);
        return;
    }

    // First pass: measure all labels to determine needed left padding
    var maxLabelW = 0;
    ctx.font = '11px sans-serif';
    labels.forEach(function(l) { var w = ctx.measureText(l).width; if (w > maxLabelW) maxLabelW = w; });
    var labelArea = Math.min(maxLabelW + 20, 250);  // cap at 250px

    // Wrap labels that exceed label area
    var wrappedLabels = labels.map(function(label) {
        ctx.font = '11px sans-serif';
        if (ctx.measureText(label).width <= labelArea - 10) {
            return { lines: [label], singleLine: true };
        }
        // Split into two lines at natural break point
        var half = Math.ceil(label.length / 2);
        var breaks = ['·', '（', '(', '）', ')', '、', '—', '-', ' '];
        for (var j = Math.max(0, half - 4); j < Math.min(label.length, half + 4); j++) {
            if (breaks.indexOf(label[j]) !== -1) { half = j + 1; break; }
        }
        return { lines: [label.slice(0, half), label.slice(half)], singleLine: false };
    });

    // Row heights
    var singleH = 28, doubleH = 38, gap = 4;
    var rowHeights = wrappedLabels.map(function(w) { return w.singleLine ? singleH : doubleH; });
    var totalH = rowHeights.reduce(function(a, b) { return a + b + gap; }, -gap);

    var pad = { top: 10, right: 50, bottom: 10, left: labelArea };
    canvas.height = Math.max(220, pad.top + totalH + pad.bottom);
    canvas.style.height = canvas.height + 'px';
    container.innerHTML = '';
    container.appendChild(canvas);

    ctx = canvas.getContext('2d');

    // All bars same width — fill the remaining space
    var barW = canvasW - pad.left - pad.right;
    var barH = 20;

    var colors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                  '#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0'];

    var y = pad.top;
    wrappedLabels.forEach(function(w, i) {
        var rowH = rowHeights[i];
        var barY = y + (rowH - barH) / 2;

        // Label — right-aligned in label area
        ctx.textAlign = 'right';
        if (w.singleLine) {
            ctx.fillStyle = '#374151';
            ctx.font = '11px sans-serif';
            ctx.fillText(w.lines[0], pad.left - 10, y + rowH / 2 + 4);
        } else {
            ctx.fillStyle = '#374151';
            ctx.font = '9px sans-serif';
            ctx.fillText(w.lines[0], pad.left - 10, y + rowH * 0.35 + 3);
            ctx.fillText(w.lines[1], pad.left - 10, y + rowH * 0.75 + 3);
        }

        // Bar — uniform width
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(pad.left, barY, barW, barH);

        // Value — right-aligned inside bar
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(values[i], pad.left + barW - 8, barY + barH / 2 + 4);

        y += rowH + gap;
    });
}
