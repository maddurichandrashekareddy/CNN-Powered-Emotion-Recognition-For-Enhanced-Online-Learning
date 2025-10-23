let pieCtx = document.getElementById('pieChart').getContext('2d');
let barCtx = document.getElementById('barChart').getContext('2d');

let labels = ['Engaged', 'Bored/Neutral', 'Confused/Frustrated', 'No Face Detected'];

let pieChart = new Chart(pieCtx, {
    type: 'pie',
    data: { 
        labels: labels, 
        datasets: [{ 
            data: [0,0,0,0], 
            backgroundColor: ['#4caf50','#ffeb3b','#f44336','#9e9e9e'] 
        }] 
    },
    options: { responsive: false }
});

let barChart = new Chart(barCtx, {
    type: 'bar',
    data: { 
        labels: labels, 
        datasets: [{ 
            label: 'Learning State Counts', 
            data: [0,0,0,0], 
            backgroundColor: ['#4caf50','#ffeb3b','#f44336','#9e9e9e'] 
        }] 
    },
    options: { responsive: false, scales: { y: { beginAtZero: true } } }
});

let videoRunning = false;

function startVideo() {
    fetch('/start').then(() => {
        document.getElementById('video').src = '/video_feed';
        videoRunning = true;
    });
}

function stopVideo() {
    fetch('/stop').then(() => {
        document.getElementById('video').src = '';
        videoRunning = false;
    });
}

// Update charts every second
setInterval(() => {
    if(videoRunning){
        fetch('/emotion_data')
        .then(res => res.json())
        .then(data => {
            let values = [
                data['Engaged'] || 0,
                data['Bored/Neutral'] || 0,
                data['Confused/Frustrated'] || 0,
                data['No Face Detected'] || 0
            ];

            pieChart.data.datasets[0].data = values;
            pieChart.update();

            barChart.data.datasets[0].data = values;
            barChart.update();
        });
    }
}, 1000);
