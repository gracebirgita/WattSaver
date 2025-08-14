const options={
            animation: true,
            maintainAspectRation: true
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

        const dataHist={
            labels: ['Jan', 'Feb', 'Mar', 'Apr'],
            datasets:[{
                    // pengeluaran aktual(dari akumulasi devices)
                    label: 'Pengeluaran aktual',
                    data:[2000000, 4000000, 2300000,3500000],
                    borderColor: '#FFE18D',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: 'Target',
                    data:[1500000, 3000000, 2200000,3200000],
                    borderColor: 'green',
                    borderWidth: 2,
                    borderDash: [5,5],
                    fill:false
                }
            ]
        }
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