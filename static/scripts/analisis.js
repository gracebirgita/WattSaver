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
        predictResultElement.style.color='#265853';
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

// filter status - table device
const filterDropdown = document.querySelectorAll('.dropdown-item');

filterDropdown.forEach( item =>{
  item.addEventListener('click', function(e){
    e.preventDefault();
    const filterValue = this.getAttribute('data-filter'); // by data-filter
    const rows = document.querySelectorAll('tbody tr');

    console.log('data-filter : ', filterValue);

    rows.forEach(row =>{
      const statusRow = row.querySelector('.status');
      console.log(statusRow); //status di table
      const statusText = statusRow ? statusRow.textContent.trim().toLowerCase() : '';
      const filterCompare = filterValue.trim().toLowerCase();

      if(filterValue === 'all' || filterCompare==statusText){
        row.style.display='';
      }
      else{
        row.style.display='none';
      }
    });

    // update dropdown label based on click
    document.getElementById('filter-status').innerHTML = `${this.textContent} &nbsp;<i class="bi bi-chevron-down"></i>`;

  });
});


// disable add device + table -> before input target & gol listrik
document.addEventListener('DOMContentLoaded', function(){
    const targetForm = document.getElementById('target-form');
    const addDeviceForm = document.getElementById('add-device-form');
    const deviceTable = document.getElementById('devices-table');

    targetForm.addEventListener('submit', function(){
        addDeviceForm.style.display='';
        deviceTable.style.display='';
    });
});

// disable analysis if table empty
document.addEventListener('DOMContentLoaded', function(){
    const deviceTable = document.getElementById('devices-table');
    const tbody = deviceTable.querySelector('tbody')
    const rows = tbody ? tbody.querySelectorAll('tr') : [];

    if(rows.length ===0){
        console.log('devices empty');
        // display tabel none
        deviceTable.style.display='none';
        
    }
    else{
        console.log('device available');
        deviceTable.style.display='';
    }
});

// ** chartjs - analisis chart
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

// const statusCounts = {{ status_counts|tojson }};
const total = statusCounts.total_rendah + statusCounts.total_sedang + statusCounts.total_tinggi;
const dataPersen = [
    total ? Math.round(statusCounts.total_rendah / total * 100) : 0,
    total ? Math.round(statusCounts.total_sedang / total * 100) : 0,
    total ? Math.round(statusCounts.total_tinggi / total * 100) : 0
];
console.log("data persen : ",dataPersen);

const data={
    labels:['Rendah', 'Sedang', 'Tinggi'],
    datasets:[{
        // data: [200, 300, 500],
        data: dataPersen,
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
