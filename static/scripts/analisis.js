// analisis section appear
const analyzeButton = document.getElementById('analisis-btn');
const predictionElement = document.getElementById('predict-result');
const recommendElement = document.getElementById('recommendation');

// get result category -> change color(red, yellow, green)
const predictResultElement = document.getElementById('predict-category');
const predictContainer = document.getElementById('prediction');
const predictResult = predictResultElement.textContent.toLowerCase().trim();

console.log('Predict result: ', predictResult);

analyzeButton.addEventListener('click', function(){
    if(predictionElement.style.display === 'none'){
        predictionElement.style.display = 'block';
        recommendElement.style.display = 'block';
    }
});


if(predictResultElement && predictContainer){
    
    if(predictResult === 'hemat'){
        predictResultElement.style.color='#219F1D';
        predictContainer.style.backgroundColor='#D2E6E4';
        recommendElement.style.display = 'none';
    }
    else if(predictResult === 'normal'){
        predictResultElement.style.color='#BA8C09';
        predictContainer.style.backgroundColor='#FFE7A6';
    }
    else if(predictResult === 'boros'){
        predictResultElement.style.color='red';
        predictContainer.style.backgroundColor='#FFC1BE';
        
    }
    else{
        console.log('category not found');
    }
}

// ** chartjs - analisis chart
const options={
    animation: true,
    maintainAspectRatio: false,
    responsive: true,
    plugins:{
        legend: {
            position: 'bottom',
        }
    }
}


const data={
    labels:['Rendah', 'Sedang', 'Tinggi'],
    datasets:[{
        data: [200, 300, 500],
            // data: [{}],
        label: 'value',
        backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        hoverOffset: 4
    }]
}

let statusElement = document.getElementById('status-chart').getContext('2d');
let statusChart = new Chart(statusElement, {
    type: 'pie', //bar, horizontalBar, pie, doughnut, radar, polarArea
    data:data,
    options: options
});
