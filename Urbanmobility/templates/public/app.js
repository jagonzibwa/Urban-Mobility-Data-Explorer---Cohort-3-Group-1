// Trip Density by Hour
//updating the chart to get data from the backend
const ctx1 = document.getElementById('trip_density_by_hour').getContext('2d');
const hourChart = new Chart(ctx1, {
  type: 'line',
  data: {
    labels: Array.from({ length: 24 }, (_, i) => `${i}h`),
    datasets: [{
      label: 'Trips per Hour',
      data: [],
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

function updateHourChart(time = 'all') {
  fetch(`/api/chart/hourly_density?time=${time}`)
    .then(res => res.json())
    .then(data => {
      hourChart.data.datasets[0].data = data.data;
      hourChart.update();
    });
}

document.getElementById('filter-hour').addEventListener('change', e => {
  updateHourChart(e.target.value);
});

updateHourChart(); // initial load

// Trip Duration Distribution
const ctx = document.getElementById('trip_duration_distribution').getContext('2d');

const durationChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'Trip Count',
      data: [],
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

function updateDurationChart(passenger = 'all') {
  const param = passenger === '3' ? '3+' : passenger;
  fetch(`/api/chart/duration_distribution?passenger=${encodeURIComponent(param)}`)
    .then(res => res.json())
    .then(data => {
      durationChart.data.labels = data.labels;
      durationChart.data.datasets[0].data = data.data;
      durationChart.update();
    })
    .catch(() => {});
}

updateDurationChart();

// Vendor Performance Comparison
const ctx3 = document.getElementById('vendor_performance_comparison').getContext('2d');
const vendorChart = new Chart(ctx3, {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'Average Fare per KM',
      data: [],
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

function updateVendorChart(vendor = 'all') {
  fetch(`/api/chart/vendor_performance?vendor=${encodeURIComponent(vendor)}`)
    .then(res => res.json())
    .then(data => {
      vendorChart.data.labels = data.labels;
      vendorChart.data.datasets[0].data = data.data;
      vendorChart.update();
    })
    .catch(() => {});
}

updateVendorChart();

//Rendering the map
const map = L.map('map-container').setView([40.7128, -74.0060], 12); // Centered on New York City
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

//adding the heatmap layer
let heatlayer = L.heatLayer([], {radius: 25}).addTo(map);

function updateHeatmap(type = 'pickup') {
  fetch(`/api/heatmap?type=${encodeURIComponent(type)}`)
    .then(res => res.json())
    .then(points => {
      // points is array of [lat, lng, intensity]
      heatlayer.setLatLngs(points);
    })
    .catch(() => {});
}

updateHeatmap('pickup');

// Hook up UI filters after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  const hourFilter = document.getElementById('filter-hour');
  if (hourFilter) {
    hourFilter.addEventListener('change', e => updateHourChart(e.target.value));
  }

  const durationFilter = document.getElementById('filter-duration');
  if (durationFilter) {
    durationFilter.addEventListener('change', e => updateDurationChart(e.target.value));
  }

  const vendorFilter = document.getElementById('filter-vendor');
  if (vendorFilter) {
    vendorFilter.addEventListener('change', e => updateVendorChart(e.target.value));
  }

  const mapType = document.getElementById('map-type');
  if (mapType) {
    mapType.addEventListener('change', e => updateHeatmap(e.target.value));
  }
});