let chart = null;
let modalInstance = new bootstrap.Modal(document.getElementById('chartModal'), {
    backdrop: true,
    keyboard: true
});

document.querySelectorAll('.summary-card').forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', async () => {
        const response = await fetch('/api/monthly-stats');
        const { success, data } = await response.json();
        
        if (!success || !data.length) {
            alert('데이터를 불러올 수 없습니다.');
            return;
        }

        if (chart) chart.destroy();
        
        const labels = data.map(d => d.month);
        const rentals = data.map(d => d.rental_count);
        const revenues = data.map(d => d.total_revenue);

        const ctx = document.getElementById('monthlyChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '월별 대여 횟수',
                    data: rentals,
                    borderColor: '#6a82fb',
                    tension: 0.3,
                    yAxisID: 'y'
                }, {
                    label: '월별 수익 (원)',
                    data: revenues,
                    borderColor: '#fc5c7d',
                    tension: 0.3,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index' },
                scales: {
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: { text: '대여 횟수', display: true }
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        title: { text: '수익 (원)', display: true },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });

        // Use the existing modal instance
        modalInstance.show();
    });
});

document.querySelectorAll('.sortable').forEach(headerCell => {
    headerCell.addEventListener('click', function() {
        const table = this.closest('table');
        const headerIndex = Array.prototype.indexOf.call(this.parentElement.children, this);
        const currentIsAscending = this.classList.contains('asc');
        
        // Reset all headers
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('asc', 'desc');
            th.innerHTML = th.innerHTML.replace('▼','').replace('▲','');
        });

        // Set new sort direction
        this.classList.toggle('asc', !currentIsAscending);
        this.classList.toggle('desc', currentIsAscending);

        sortTable(table, headerIndex, currentIsAscending ? 'desc' : 'asc');
    });
});

function sortTable(table, column, direction) {
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const dataType = table.querySelectorAll('th')[column].dataset.sort;

    rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();

        if (dataType === 'number') {
            const numA = parseFloat(aValue.replace(/[^0-9.]/g, ''));
            const numB = parseFloat(bValue.replace(/[^0-9.]/g, ''));
            return direction === 'asc' ? numA - numB : numB - numA;
        } else {
            return direction === 'asc' 
                ? aValue.localeCompare(bValue, 'ko', { sensitivity: 'base' })
                : bValue.localeCompare(aValue, 'ko', { sensitivity: 'base' });
        }
    });

    // Rebuild table
    rows.forEach(row => tbody.appendChild(row));
}
document.addEventListener("DOMContentLoaded", () => {
    const tables = document.querySelectorAll("table");

    tables.forEach(table => {
        const headers = table.querySelectorAll("th.sortable");

        headers.forEach(header => {
            let ascending = true;
            header.addEventListener("click", () => {
                const columnIndex = [...header.parentNode.children].indexOf(header);
                const rows = Array.from(table.querySelectorAll("tbody tr")).filter(row => !row.classList.contains("no-data"));

                // 정렬
                rows.sort((a, b) => {
                    const aText = a.children[columnIndex].innerText.replace(/,/g, '');
                    const bText = b.children[columnIndex].innerText.replace(/,/g, '');
                    const aValue = isNaN(aText) ? aText : parseFloat(aText);
                    const bValue = isNaN(bText) ? bText : parseFloat(bText);
                    return ascending ? aValue - bValue : bValue - aValue;
                });

                // tbody 재정렬
                const tbody = table.querySelector("tbody");
                rows.forEach(row => tbody.appendChild(row));

                // 다른 화살표 초기화
                headers.forEach(h => h.innerHTML = h.innerText.split(" ")[0] + " ▼");

                // 현재 정렬 상태 아이콘 변경
                header.innerHTML = header.innerText.split(" ")[0] + (ascending ? " ▲" : " ▼");

                ascending = !ascending;
            });
        });
    });
});
