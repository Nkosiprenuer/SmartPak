// JavaScript logic for fetching and displaying client records
document.addEventListener('DOMContentLoaded', function () {
    fetchClientRecords();
});

function fetchClientRecords() {
    fetch('/client_records')
        .then(response => response.json())
        .then(data => {
            const recordsContainer = document.getElementById('records-container');
            recordsContainer.innerHTML = ''; // Clear previous records
            data.forEach(record => {
                const recordElement = document.createElement('div');
                recordElement.innerHTML = `
                    <p>Plate Text: ${record.plate_text}</p>
                    <p>Capture Date: ${record.capture_date}</p>
                    <p>Capture Time: ${record.capture_time}</p>
                    <p>Cost: $${record.cost}</p>
                `;
                recordsContainer.appendChild(recordElement);
            });
        })
        .catch(error => console.error('Error fetching client records:', error));
}
