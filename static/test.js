document.getElementById('portfolioForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    console.log("Submitting form...");
    let formData = new FormData(this);
    
    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Received JSON Data:", data);
        
        if (!data.portfolio_returns || !data.benchmark_returns) {
            alert("Error: Portfolio data is missing!");
            return;
        }

        document.getElementById('portfolioRisk').textContent = data.portfolio_risk;
        
        let dates = Object.keys(data.portfolio_returns);
        let portfolioValues = Object.values(data.portfolio_returns);
        let benchmarkValues = Object.values(data.benchmark_returns);

        let tracePortfolio = {
            x: dates,
            y: portfolioValues,
            type: 'scatter',
            mode: 'lines',
            name: 'Portfolio',
            line: { color: 'orange' }
        };

        let traceBenchmark = {
            x: dates,
            y: benchmarkValues,
            type: 'scatter',
            mode: 'lines',
            name: 'S&P 500',
            line: { color: 'blue' }
        };

        let layout = {
            title: 'Portfolio vs S&P 500 Cumulative Returns',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Cumulative Return' },
            template: 'plotly_dark'
        };

        Plotly.newPlot('returnsChart', [tracePortfolio, traceBenchmark], layout);

        let pieData = [{
            labels: data.assets,
            values: data.weights,
            type: 'pie',
            hole: 0.4,
            textinfo: 'label+percent'
        }];

        let pieLayout = {
            title: 'Portfolio Asset Allocation',
            template: 'plotly_dark'
        };

        Plotly.newPlot('pieChart', pieData, pieLayout);
    })
    .catch(error => console.error('Error:', error));
});
