let balanceChart = null;
let distributionChart = null;

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        updateStatus(true);
        updateKPIs(data);
        updateChart(data.history);
        updateActivePositions(data.open_positions);
        updateRecentTrades(data.recent_trades);
    } catch (error) {
        console.error('Error fetching stats:', error);
        updateStatus(false);
    }
}

function updateStatus(connected) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (connected) {
        dot.className = 'dot green';
        text.textContent = 'Live';
    } else {
        dot.className = 'dot red';
        text.textContent = 'Offline (Retrying...)';
    }
}

function updateKPIs(data) {
    document.getElementById('kpi-balance').textContent = `$${data.balance.toFixed(2)}`;
    
    const pnlEl = document.getElementById('kpi-pnl');
    pnlEl.textContent = `${data.total_pnl >= 0 ? '+' : ''}$${data.total_pnl.toFixed(2)}`;
    pnlEl.className = `kpi-value ${data.total_pnl >= 0 ? 'text-success' : 'text-danger'}`;
    
    document.getElementById('kpi-winrate').textContent = `${data.win_rate}%`;
    
    document.getElementById('kpi-open').textContent = data.open_positions.length;
    document.getElementById('active-count').textContent = data.open_positions.length;
    
    updateDistributionChart(data.balance, data.invested_capital);
}

function updateDistributionChart(balance, invested) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    
    if (distributionChart) {
        distributionChart.data.datasets[0].data = [balance, invested];
        distributionChart.update();
    } else {
        distributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Liquidez (Efectivo)', 'Capital Invertido'],
                datasets: [{
                    data: [balance, invested],
                    backgroundColor: ['#8a2be2', '#00ffff'],
                    borderColor: ['rgba(0,0,0,0)', 'rgba(0,0,0,0)'],
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#f0f0f0', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }
}

function updateChart(history) {
    if (history.length === 0) return;
    
    const ctx = document.getElementById('balanceChart').getContext('2d');
    const labels = history.map(h => {
        const d = new Date(h.time + 'Z');
        return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    });
    const dataPoints = history.map(h => h.balance);

    if (balanceChart) {
        balanceChart.data.labels = labels;
        balanceChart.data.datasets[0].data = dataPoints;
        balanceChart.update();
    } else {
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.font.family = 'Inter';
        
        let gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(138, 43, 226, 0.5)');
        gradient.addColorStop(1, 'rgba(138, 43, 226, 0.0)');

        balanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Balance (USD)',
                    data: dataPoints,
                    borderColor: '#8a2be2',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointBackgroundColor: '#00ffff',
                    pointBorderColor: '#8a2be2',
                    pointRadius: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

function updateActivePositions(positions) {
    const tbody = document.getElementById('active-tbody');
    if (positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay inversiones activas. Esperando a Gemini...</td></tr>';
        return;
    }
    
    tbody.innerHTML = positions.map(p => {
        const d = new Date(p.time + 'Z');
        return `
            <tr>
                <td>${p.title}</td>
                <td class="decision-${p.decision.toLowerCase()}">${p.decision}</td>
                <td>$${p.invested.toFixed(2)}</td>
                <td class="text-muted">${d.toLocaleDateString()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}</td>
            </tr>
        `;
    }).join('');
}

function updateRecentTrades(trades) {
    const tbody = document.getElementById('recent-tbody');
    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Aún no hay resoluciones.</td></tr>';
        return;
    }
    
    tbody.innerHTML = trades.map(t => {
        const pnlClass = t.pnl > 0 ? 'text-success' : 'text-danger';
        const pnlText = t.pnl > 0 ? `+$${t.pnl.toFixed(2)}` : `-$${Math.abs(t.pnl).toFixed(2)}`;
        return `
            <tr>
                <td><div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px;" title="${t.title}">${t.title}</div></td>
                <td class="decision-${t.decision.toLowerCase()}">${t.decision}</td>
                <td class="${pnlClass}">${pnlText}</td>
            </tr>
        `;
    }).join('');
}

// Fetch stats every 5 seconds
fetchStats();
setInterval(fetchStats, 5000);
