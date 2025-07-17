document.getElementById('optionForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const S = document.getElementById('S').value;
    const K = document.getElementById('K').value;
    const T = document.getElementById('T').value;
    const r = document.getElementById('r').value;
    const vol = document.getElementById('vol').value;

    try {
        const response = await fetch('/BSM/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ S, K, T, r, vol }),
        });

        if (response.ok) {
            const data = await response.json(); 
            console.log("Response Data:", data);

            if (data.result && data.result['call-option'] && data.result['put-option']) {
                document.getElementById('call-option').textContent = `Call Option Price: ${data.result['call-option']}`;
                document.getElementById('put-option').textContent = `Put Option Price: ${data.result['put-option']}`;
            } else {
                alert('Unexpected response structure');
            }
        } else {
            alert('Failed to calculate option prices. Please check your input.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing your request.');
    }
});
