// Trip Density by Hour
//updating the chart to get data from the backend
const ctx1 = document.getElementById('trip_density_by_hour').getContext('2d');
new Chart(ctx1, {
  type: 'line',
  data: {
    labels: ['0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h', '20h', '21h', '22h', '23h'],
    datasets: [{
      label: 'Trips per Hour',
      data: [120, 80, 60, 40, 30, 50, 100, 300, 500, 600, 700, 800, 750, 720, 680, 650, 700, 900, 850, 600, 400, 300, 200, 150],
      borderColor: 'rgba(75, 192, 192, 1)',
      fill: false,
      tension: 0.3
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Trip Density by Hour'
      }
    }
  }
});

// Trip Duration Distribution
const ctx = document.getElementById('trip_duration_distribution').getContext('2d');

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['0–5 min', '5–10 min', '10–15 min', '15–20 min', '20–30 min', '30+ min'], // duration bins
    datasets: [{
      label: 'Trip Count',
      data: [150, 300, 250, 200, 100, 50], // frequency per bin
      backgroundColor: 'rgba(255, 159, 64, 0.6)',
      borderColor: 'rgba(255, 159, 64, 1)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Trip Duration Histogram'
      },
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Trip Duration (minutes)'
        },
        grid: {
          display: false
        },
        ticks: {
          autoSkip: false
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Trips'
        }
      }
    },
    elements: {
      bar: {
        borderSkipped: false,
        barPercentage: 1.0,
        categoryPercentage: 1.0
      }
    }
  }
});

// Vendor Performance Comparison
const ctx3 = document.getElementById('vendor_performance_comparison').getContext('2d');
new Chart(ctx3, {
  type: 'bar',
  data: {
    labels: ['Vendor A', 'Vendor B'],
    datasets: [{
      label: 'Average Fare per KM',
      data: [2.5, 3.1],
      backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)'],
      borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Vendor Performance Comparison'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

//Rendering the map
const map = L.map('map-container').setView([40.7128, -74.0060], 12); // Centered on New York City
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

//adding the heatmap layer
let heatlayer = L.heatLayer([], {radius: 25}).addTo(map);
