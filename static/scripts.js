let currentChartData = [];

document.addEventListener("DOMContentLoaded", function () {
    loadPortfolioAndChart();
});

// Fetch both portfolio data and graph together
function loadPortfolioAndChart() {
    Promise.all([
        fetchPortfolio(),
        fetchgraph()
    ]).catch(error => console.error("Error loading portfolio and graph:", error));
}
function fetchPortfolio(){
    fetch('/PV/api/portfolio')
    .then(response=>response.json())
    .then(data =>{
    console.log("Portfolio Data:", data);
    let table=document.getElementById('portfolioTable');
    if (!Array.isArray(data)) {
        console.error("Expected an array but got:", typeof data, data);
        return;
    }
    let tbody = table.getElementsByTagName('tbody')[0];
    tbody.innerHTML=''

    data.forEach(stock => {
        let row=tbody.insertRow();
        row.innerHTML=`
        <tr>
            <td>${stock.ticker}</td>
            <td>${stock.amount}</td>
            <td>${parseFloat(stock.purchase_price).toFixed(2)}</td>
            <td>${parseFloat(stock.current_price).toFixed(2)}</td>
            <td>${parseFloat(stock.profit_loss).toFixed(2)}</td>
            <td>
                <button onclick="updateStock('${stock.ticker}')">Update</button>
            </td>
        </tr>
        `;
    });
}).catch(error => console.error("Error fetching portfolio:", error));
}
function fetchgraph(){
    fetch('/PV/api/portfolio-chart')
        .then(response => response.json())
        .then(data => {
            currentChartData = data;
            drawChart(currentChartData);
        })
        .catch(error => console.error('Error loading chart:', error)
    );
}
async function addStock(){
    const ticker = document.getElementById("ticker").value;
    const amount = document.getElementById('amount').value;

    await fetch("/PV/api/portfolio",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ticker, amount: parseInt(amount)}),
    });

    fetchPortfolio();
    plotPortfolio();
}

async function plotPortfolio(){
    const response = await fetch("/PV/api/portfolio-chart")
    const graphJSON = await response.json();

    const chartDiv = document.getElementById('chart');
    if (chartDiv.data){
        Plotly.react(chartDiv,graphJSON.data,graphJSON.layout);
    }
    else{
        Plotly.newPlot('chart',graphJSON.data,graphJSON.layout);
    }
}

window.onload = async () => {
    await loadPortfolioAndChart();
}

async function updateStock(ticker){
    const newAmount = prompt(`Enter the new amount for ${ticker}: `)
    if (newAmount){
        const responce=await fetch(`/PV/api/portfolio/${ticker}`,{
            method: "PUT",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({amount: parseInt(newAmount)})
        });

        const data = await responce.json();
        if(responce.ok){
            alert(data.message)
            await fetchPortfolio();
            await plotPortfolio();
        }
        else{
            alert(data.error)
        }
        
    }
}

function drawChart(data) {
    let chartWidth = window.innerWidth > 1200 ? 800 : (window.innerWidth * 0.8);
    let chartHeight = window.innerHeight > 800 ? 500 : (window.innerHeight * 0.5);

    let layout = {
        title: 'Portfolio Overview',
        height: chartHeight,
        width: chartWidth
    };

    Plotly.newPlot('chart', data, layout);
}

// Resize chart when window resizes
window.addEventListener('resize', () => {
    drawChart(currentChartData); // Make sure to store the latest data globally
});

