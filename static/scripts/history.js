// history label
const predictLabel = document.querySelectorAll('.category-label');

predictLabel.forEach(label =>{
    const strongElement = label.querySelector('strong')
    if (!strongElement) return;
    const textLabel = strongElement.textContent.toLowerCase().trim()
    console.log(textLabel)

    if(textLabel==='boros'){
        strongElement.style.color='red';
    }
    else if(textLabel==='normal'){
        strongElement.style.color = '#BA8C09';
    }
    else if(textLabel==='hemat'){
        strongElement.style.color ='#265853';
    }
})



const options={
            animation: true,
            maintainAspectRation: true
        }
        const labels = rumahList.map(rumah => namaBulan[parseInt(rumah[1])] + ' ' + rumah[2]);
        const pengeluaranAktual = rumahList.map(rumah => rumah[4]);
        const target = rumahList.map(rumah => rumah[3]);
                
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

        const dataHist = {
            labels: labels,
            datasets: [
                {
                    label: 'Pengeluaran aktual',
                    data: pengeluaranAktual,
                    borderColor: '#FFE18D',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3
                },
                {
                    label: 'Target',
                    data: target,
                    borderColor: 'green',
                    borderWidth: 2,
                    borderDash: [5,5],
                    fill: false,
                    tension: 0.3
                }
            ]
        };
        let chart2 = document.getElementById('history-chart').getContext('2d');

        let historyChart = new Chart(chart2,{
            type: 'line',
            data: dataHist,

            options:{
                responsive: true,
                plugins:{
                    title:{
                        display: true,
                        text: 'Pengeluaran vs Target'
                    }
                },
                scales:{
                    x:{
                        title:{
                            display: true,
                            text: 'x (bulan)',
                            font:{
                                size: 14
                            }
                        }
                    },

                    y:{
                        title:{
                            display:true,
                            text: 'y (pengeluaran [Rp])',
                            font:{
                                size:14
                            }
                        },
                        grid:{
                            display: true,
                            lineWidth: 2,
                        }
                    }
                }
            }
        });