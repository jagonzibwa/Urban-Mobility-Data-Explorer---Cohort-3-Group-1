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
  console.log(`Updating hour chart for time: ${time}`);
  fetch(`/api/chart/hourly_density?time=${time}`)
    .then(res => res.json())
    .then(data => {
      console.log('Hour chart data:', data);
      hourChart.data.datasets[0].data = data.data;
      hourChart.update();
    })
    .catch(err => console.error('Error fetching hour data:', err));
}

// Wait for DOM to be ready before adding event listeners
document.addEventListener('DOMContentLoaded', function() {
  const hourFilter = document.getElementById('filter-hour');
  if (hourFilter) {
    hourFilter.addEventListener('change', e => {
      console.log('Hour filter changed to:', e.target.value);
      updateHourChart(e.target.value);
    });
  }
});

updateHourChart(); // initial load

// Trip Duration Distribution
const ctx = document.getElementById('trip_duration_distribution').getContext('2d');
const durationChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['0–5 min', '5–10 min', '10–15 min', '15–20 min', '20–30 min', '30+ min'],
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
        text: 'Trip Duration Distribution'
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
  console.log(`Updating duration chart for passenger: ${passenger}`);
  fetch(`/api/chart/duration_distribution?passenger=${passenger}`)
    .then(res => res.json())
    .then(data => {
      console.log('Duration chart data:', data);
      durationChart.data.datasets[0].data = data.data;
      durationChart.update();
    })
    .catch(err => console.error('Error fetching duration data:', err));
}

// Wait for DOM to be ready before adding event listeners
document.addEventListener('DOMContentLoaded', function() {
  const durationFilter = document.getElementById('filter-duration');
  if (durationFilter) {
    durationFilter.addEventListener('change', e => {
      console.log('Duration filter changed to:', e.target.value);
      updateDurationChart(e.target.value);
    });
  }
});

updateDurationChart(); // initial load

// Vendor Performance Comparison
const ctx3 = document.getElementById('vendor_performance_comparison').getContext('2d');
const vendorChart = new Chart(ctx3, {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'Average Fare per KM',
      data: [],
      backgroundColor: 'rgba(54, 162, 235, 0.6)',
      borderColor: 'rgba(54, 162, 235, 1)',
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
        beginAtZero: true,
        title: {
          display: true,
          text: 'Fare per KM ($)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Vendor'
        }
      }
    }
  }
});

function updateVendorChart(vendor = 'all') {
  console.log(`Updating vendor chart for vendor: ${vendor}`);
  fetch(`/api/chart/vendor_performance?vendor=${vendor}`)
    .then(res => res.json())
    .then(data => {
      console.log('Vendor chart data:', data);
      vendorChart.data.labels = data.labels;
      vendorChart.data.datasets[0].data = data.data;
      vendorChart.update();
    })
    .catch(err => console.error('Error fetching vendor data:', err));
}

// Wait for DOM to be ready before adding event listeners
document.addEventListener('DOMContentLoaded', function() {
  const vendorFilter = document.getElementById('filter-vendor');
  if (vendorFilter) {
    vendorFilter.addEventListener('change', e => {
      console.log('Vendor filter changed to:', e.target.value);
      updateVendorChart(e.target.value);
    });
  }
});

updateVendorChart(); // initial load

// Rendering the map
const map = L.map('map-container').setView([40.7128, -74.0060], 12); // Centered on New York City
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Adding the heatmap layer - using simple markers if heatmap library fails
let heatmapData = [];
let markers = L.layerGroup().addTo(map);

function updateHeatmap(type = 'pickup') {
  console.log(`Updating heatmap for ${type}...`);
  
  fetch(`/api/heatmap?type=${type}`)
    .then(res => res.json())
    .then(data => {
      console.log(`Received ${data.length} heatmap points`);
      
      // Clear existing markers
      map.removeLayer(markers);
      markers = L.layerGroup();
      
      // Add markers for each point
      data.forEach(point => {
        if (point && point.length >= 2) {
          const [lat, lng, intensity] = point;
          const marker = L.circleMarker([lat, lng], {
            radius: Math.max(2, Math.min(10, intensity / 10)), // Scale radius based on intensity
            fillColor: intensity > 20 ? '#ff0000' : intensity > 10 ? '#ff8800' : '#ffff00',
            color: '#000',
            weight: 1,
            opacity: 0.8,
            fillOpacity: 0.6
          });
          
          marker.bindPopup(`${type} location<br>Intensity: ${intensity}`);
          markers.addLayer(marker);
        }
      });
      
      markers.addTo(map);
      console.log(`Added ${data.length} markers to map`);
    })
    .catch(err => {
      console.error('Error fetching heatmap data:', err);
      // Add a simple marker to show the map is working
      L.marker([40.7128, -74.0060]).addTo(map)
        .bindPopup('Heatmap data loading failed, but map is working!')
        .openPopup();
    });
}

// Wait for DOM to be ready before adding event listeners
document.addEventListener('DOMContentLoaded', function() {
  const mapTypeSelect = document.getElementById('map-type');
  if (mapTypeSelect) {
    mapTypeSelect.addEventListener('change', e => {
      updateHeatmap(e.target.value);
    });
  }
});

updateHeatmap(); // initial load

// Load dashboard statistics
function loadDashboardStats() {
  console.log('Loading dashboard statistics...');
  fetch('/api/stats/summary')
    .then(res => res.json())
    .then(data => {
      console.log('Dashboard stats:', data);
      // Update the home section with real statistics
      const homeSection = document.querySelector('#home ul');
      if (homeSection && data.total_trips) {
        homeSection.innerHTML = `
          <li><p>Over ${data.total_trips.toLocaleString()}+ trips analyzed</p></li>
          <li><p>${data.total_vendors} vendors tracked</p></li>
          <li><p>${data.total_locations} unique locations</p></li>
          <li><p>Average trip duration: ${Math.round(data.avg_trip_duration / 60)} minutes</p></li>
          <li><p>Average speed: ${data.avg_speed} mph</p></li>
          <li><p>Average fare: $${data.avg_fare_per_km}/km</p></li>
        `;
      }
    })
    .catch(err => console.error('Error fetching dashboard stats:', err));
}

// Wait for DOM to be ready before loading stats
document.addEventListener('DOMContentLoaded', function() {
  loadDashboardStats();
});
