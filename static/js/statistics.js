/**
 * 竞享成果 - 统计图表 (原生 Canvas 实现)
 */

document.addEventListener('DOMContentLoaded', function() {
    loadOverview();
    loadByLevel();
    loadByCompetition();
    loadByClass();
});

function loadOverview() {
    fetch('/api/admin/statistics/overview', { credentials: 'same-origin' })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            document.getElementById('stat-total').textContent = d.total;
            document.getElementById('stat-pending').textContent = d.pending;
            document.getElementById('stat-approved').textContent = d.approved;
            document.getElementById('stat-students').textContent = d.student_count;
        });
}

function loadByLevel() {
    fetch('/api/admin/statistics/by-level', { credentials: 'same-origin' })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            drawBarChart('chart-level', data, 'level', 'count',
                { '国家级': '#6d28d9', '省级': '#1d4ed8', '校级': '#4b5563' });
        });
}

function loadByCompetition() {
    fetch('/api/admin/statistics/by-competition?limit=10', { credentials: 'same-origin' })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var labels = data.map(function(d) {
                var label = d.name.length > 10 ? d.name.slice(0, 10) + '...' : d.name;
                return label;
            });
            var values = data.map(function(d) { return d.count; });
            drawHorizontalBarChart('chart-competition', labels, values);
        });
}

function loadByClass() {
    fetch('/api/admin/statistics/by-class', { credentials: 'same-origin' })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            drawBarChart('chart-class', data, 'class_name', 'count',
                {});
        });
}

/**
 * Vertical bar chart
 */
function drawBarChart(containerId, data, labelKey, valueKey, colorMap) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 350;
    canvas.height = 220;
    canvas.style.width = '100%';
    canvas.style.height = '220px';
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
    var padding = { top: 20, right: 20, bottom: 40, left: 50 };
    var chartW = canvas.width - padding.left - padding.right;
    var chartH = canvas.height - padding.top - padding.bottom;

    var maxVal = Math.max.apply(null, data.map(function(d) { return d[valueKey]; }));
    maxVal = Math.ceil(maxVal * 1.2 / 5) * 5 || 10;
    var barWidth = Math.min(60, chartW / data.length * 0.7);
    var gap = (chartW - barWidth * data.length) / (data.length + 1);

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
        var y = padding.top + chartH - barH;

        var defaultColors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                             '#f59e0b', '#f97316', '#ef4444', '#8b5cf6', '#10b981'];
        var color = colorMap[d[labelKey]] || defaultColors[i % defaultColors.length];

        ctx.fillStyle = color;
        ctx.fillRect(x, y, barWidth, barH);

        // Value on top
        ctx.fillStyle = '#1f2937';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(d[valueKey], x + barWidth / 2, y - 6);

        // Label below
        ctx.fillStyle = '#4b5563';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        var label = (d[labelKey] || '') .length > 6 ? (d[labelKey] || '').slice(0, 5) + '..' : (d[labelKey] || '');
        ctx.fillText(label, x + barWidth / 2, padding.top + chartH + 16);
    });
}

/**
 * Horizontal bar chart for competition names
 */
function drawHorizontalBarChart(containerId, labels, values) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 350;
    canvas.height = Math.max(220, labels.length * 32);
    canvas.style.width = '100%';
    canvas.style.height = canvas.height + 'px';
    container.innerHTML = '';
    container.appendChild(canvas);

    if (!labels || labels.length === 0) {
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#9ca3af';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('暂无数据', canvas.width / 2, canvas.height / 2);
        return;
    }

    var ctx = canvas.getContext('2d');
    var padding = { top: 10, right: 40, bottom: 10, left: 110 };
    var chartW = canvas.width - padding.left - padding.right;
    var barH = Math.min(24, (canvas.height - padding.top - padding.bottom) / labels.length - 4);
    var gap = 4;

    var maxVal = Math.max.apply(null, values);
    maxVal = Math.ceil(maxVal * 1.15);

    labels.forEach(function(label, i) {
        var y = padding.top + i * (barH + gap);
        var w = (values[i] / maxVal) * chartW;

        // Label
        ctx.fillStyle = '#374151';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(label, padding.left - 8, y + barH / 2 + 3);

        // Bar
        var colors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                      '#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0'];
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(padding.left, y, w, barH);

        // Value
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(values[i], padding.left + w + 6, y + barH / 2 + 3);
    });
}
