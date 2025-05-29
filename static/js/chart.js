document.addEventListener('DOMContentLoaded', function() {
    fetch('/weekly-sales')
        .then(response => response.json())
        .then(data => {
            // Update revenue header values
            document.querySelector('.current-week h4').textContent = data.current_week || 'N/A';
            document.querySelector('.previous-week h4').textContent = data.previous_week || 'N/A';

            // Check if data exists and is formatted correctly
            if (!data.labels || !data.revenue) {
                console.error("Data format is incorrect or missing.");
                return;
            }

            const ctx = document.getElementById('revenueChart').getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Revenue',
                        data: data.revenue,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 5,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    aspectRatio: 2.5,
                    scales: {
                        x: {
                            title: { 
                                display: true, 
                                text: 'Week',
                                font: {
                                    size: 14
                                }
                            },
                            grid: { display: false }
                        },
                        y: {
                            title: { 
                                display: true, 
                                text: 'Revenue ($)',
                                font: {
                                    size: 14
                                }
                            },
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(200, 200, 200, 0.1)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    layout: {
                        padding: {
                            left: 20,
                            right: 20,
                            top: 20,
                            bottom: 20
                        }
                    }
                }
            });
        })
        .catch(error => console.error("Failed to fetch data:", error));
});