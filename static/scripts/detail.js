document.addEventListener('DOMContentLoaded', function(){
    const predictResultElement = document.getElementById('predict-category');
    const predictContainer = document.getElementById('prediction');
    const predictResult = predictResultElement.textContent.toLowerCase().trim();

    if(predictResult === 'hemat'){
        predictResultElement.style.color='#219F1D';
        predictContainer.style.backgroundColor='#D2E6E4';
    }
    else if(predictResult === 'normal'){
        predictResultElement.style.color='#BA8C09';
        predictContainer.style.backgroundColor='#FFE7A6';
    }
    else if(predictResult === 'boros'){
        predictResultElement.style.color='red';
        predictContainer.style.backgroundColor='#FFC1BE';
    }

    // chart
    const options={
        animation: true,
        maintainAspectRatio: false,
        responsive: true,
        plugins:{
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding : 40,

                }
            },

            tooltip:{
                callbacks:{
                    label: function(context){
                        const label = context.label
                        const value = context.raw;
                        return `${label}: ${value}%`;
                    }
                }
            }
        }
    }

    const data={
        labels:['Rendah', 'Sedang', 'Tinggi'],
        datasets:[{
            data: [200, 300, 500],
            // data: dataPersen,
                // data: [{}],
            label: 'persentase',
            backgroundColor: [
                '#FEE0E0',
                '#E6F4FE',
                '#FDF0D7'
            ],
            hoverOffset: 4
        }],

        options:{
            layout:{
                padding:{
                    bottom: 40
                }
            }
        }
    }

let statusElement = document.getElementById('status-chart').getContext('2d');
let statusChart = new Chart(statusElement, {
    type: 'pie', //bar, horizontalBar, pie, doughnut, radar, polarArea
    data:data,
    options: options
});

    // let statusElement = document.getElementById('status-chart').getContext('2d');
    // let statusChart = new Chart(statusElement, {
    //     type: 'pie', //bar, horizontalBar, pie, doughnut, radar, polarArea
    //     data:data,
    //     options: options
    // });
});
