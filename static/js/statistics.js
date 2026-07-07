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

function loadByCompetition() {
    fetchJSON('/api/admin/statistics/by-competition?limit=10')
        .then(function(data) {
            // 传完整竞赛名称，由绘图函数自行处理换行
            var labels = data.map(function(d) { return d.name; });
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
 * Long names auto-wrap to two lines with smaller font
 */
function drawHorizontalBarChart(containerId, labels, values) {
    var container = document.getElementById(containerId);
    if (!container) return;

    // Use wider canvas so labels and bars have room; container scrolls if needed
    container.style.overflowX = 'auto';
    var minWidth = 500;
    var canvasWidth = Math.max(container.clientWidth || 350, minWidth);

    var canvas = document.createElement('canvas');
    canvas.width = canvasWidth;
    canvas.style.display = 'block';
    var ctx = canvas.getContext('2d');
    if (!ctx) { container.innerHTML = '<div style="text-align:center;padding:20px;color:#9ca3af;">浏览器不支持 Canvas</div>'; return; }

    if (!labels || labels.length === 0) {
        canvas.height = 220;
        ctx.fillStyle = '#9ca3af';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('暂无数据', canvas.width / 2, canvas.height / 2);
        canvas.style.width = '100%';
        canvas.style.height = '220px';
        container.innerHTML = '';
        container.appendChild(canvas);
        return;
    }

    // Left area width for labels — enough for ~13 Chinese chars
    var labelAreaWidth = 140;

    // Determine which labels need wrapping and split them
    var wrappedLabels = labels.map(function(label) {
        ctx.font = '11px sans-serif';
        var fullWidth = ctx.measureText(label).width;
        if (fullWidth <= labelAreaWidth - 10) {
            return { lines: [label], singleLine: true };
        }
        // Need two lines — split Chinese text roughly in half
        // Also try splitting at a natural boundary like · or （
        var half = Math.ceil(label.length / 2);
        // Look for natural break points near the middle
        var breakChars = ['·', '（', '(', '）', ')', '、', '—', '-', ' '];
        var best = half;
        for (var j = Math.max(0, half - 4); j < Math.min(label.length, half + 4); j++) {
            if (breakChars.indexOf(label[j]) !== -1) { best = j + 1; break; }
        }
        // If no natural break found, just split at half (character boundary)
        if (best === half) {
            best = Math.ceil(label.length / 2);
        }
        var line1 = label.slice(0, best);
        var line2 = label.slice(best);
        return { lines: [line1, line2], singleLine: false };
    });

    // Calculate row heights
    var singleRowH = 28;
    var doubleRowH = 38;
    var gap = 4;
    var totalHeight = 0;
    var rowHeights = wrappedLabels.map(function(w) {
        var h = w.singleLine ? singleRowH : doubleRowH;
        totalHeight += h + gap;
        return h;
    });
    totalHeight -= gap; // remove last gap

    var padding = { top: 10, right: 40, bottom: 10, left: labelAreaWidth };
    canvas.height = Math.max(220, padding.top + totalHeight + padding.bottom);
    canvas.style.height = canvas.height + 'px';
    container.innerHTML = '';
    container.appendChild(canvas);

    // Re-create context after canvas resize
    ctx = canvas.getContext('2d');
    var chartW = canvas.width - padding.left - padding.right;

    var maxVal = Math.max.apply(null, values);
    maxVal = Math.ceil(maxVal * 1.15) || 1;

    // Get bar colors (more colors for differentiation)
    var barColors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                     '#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0'];

    var currentY = padding.top;
    wrappedLabels.forEach(function(w, i) {
        var rowH = rowHeights[i];
        var barH = Math.min(w.singleLine ? 22 : 28, rowH - 6);
        var wVal = (values[i] / maxVal) * chartW;

        // Center the bar vertically in this row
        var barY = currentY + (rowH - barH) / 2;

        // Draw label (one or two lines)
        ctx.textAlign = 'right';
        if (w.singleLine) {
            ctx.fillStyle = '#374151';
            ctx.font = '11px sans-serif';
            ctx.fillText(w.lines[0], padding.left - 10, currentY + rowH / 2 + 4);
        } else {
            ctx.fillStyle = '#374151';
            ctx.font = '9px sans-serif';
            ctx.fillText(w.lines[0], padding.left - 10, currentY + rowH * 0.35 + 3);
            ctx.fillText(w.lines[1], padding.left - 10, currentY + rowH * 0.75 + 3);
        }

        // Bar
        ctx.fillStyle = barColors[i % barColors.length];
        ctx.fillRect(padding.left, barY, wVal, barH);

        // Value
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(values[i], padding.left + wVal + 6, barY + barH / 2 + 4);

        currentY += rowH + gap;
    });
}
