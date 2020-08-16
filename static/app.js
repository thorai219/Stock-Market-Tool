function processForm(evt) {
  evt.preventDefault();

  const userInputs = {
    name: $("#search-term").val()
  }

  axios.post('/api/stock/chart', userInputs)
  .then(function (response) {
    displayLineChart(response)
    displayVolumeChart(response)
    appendNews(response)
  })
  .catch(function (error) {
    console.log(error)
  });
};

function displayLineChart(res) {
  const result = res.data;
  var lineChart = document.getElementById('line-chart').getContext('2d');

  let date = [];
  let price = [];
  let sma = [];

  result.sma.map((item) => {
    sma.unshift(item.sma)
  })

  result.stock.map((item) => {
    date.unshift(item.date);
    price.unshift(item.price);
  });
    var data = {
      labels: [...date],
      datasets: [{
        label: "Price",
        fill: false,
        borderColor: "black",
        borderWidth: 2.5,
        data: [...price],
      },{
        label: "SMA",
        fill: false,
        borderColor: "blue",
        borderWidth: 1.5,
        data: [...sma]
      }]
    };
    
    var options = {
      responsive: true,
      legend: {
        display: true,
      },
      title: {
        display: true,
        text: result.company.name
      },
      maintainAspectRatio: false,
      elements: { 
          point: {
            radius: 0,
            hitRadius: 10, 
            hoverRadius: 3
            } 
      }, 
      scales: {
        yAxes: [{

        }],
        xAxes: [{
          ticks: {
              display: false
          },
        }]
      }
    }
  
    var newChart = new Chart(lineChart, {
      type: "line",
      data: data,
      options: options
    })
  
  $("#desc").append(
    `
    <h3">Name: ${result.company.name},
    Exchange: ${result.company.exchange},    
    Industry: ${result.company.industry}</h3>
    `
  )
};

function appendNews(res) {
  const result = res.data.news;
  result.forEach(item => {
    if (item.urlToImage === null) {
      item.urlToImage = "/img/stock_chart.jpg"
    }
    else {
      $("#news").append(
        `<li class="card mb-4 bg-light border-dark">
          <a href="${item.url}>
            <div class="card">
              <div class="row no-gutters">
                <div class="col-sm-3">
                    <img src="${item.urlToImage}" class="img-fluid" alt="">
                </div>
                <div class="col-sm-9 mt-2">
                  <div class="card-block px-2">
                      <h4 class="card-title">${item.title}</h4>
                      <p class="card-text">${item.description}</p>
                      <p class="text-muted"><small>${item.publishedAt}</small></p>
                  </div>
                </div>
              </div>
            </div>  
          </a>
        </li>`
      )
    }
  })
}

function displayVolumeChart(res) {

  const result = res.data
  let date = [];
  let volume = [];
  result.stock.map((item) => {
    date.unshift(item.date);
    volume.unshift(item.volume);
  });

  var volumeChart = document.getElementById('volume-chart').getContext('2d');

  var myChart = new Chart(volumeChart, {
    type: 'bar',
    data: 
    {
      labels: [...date],
      datasets: [
        {
          label: "Volume",
          data: [...volume],
          fill: false,
          borderColor: ['black'],
          borderWidth: 2.5
        },
      ]
    },
      options: {
      legend: {
        display: false
      },   
      maintainAspectRatio: false,
      elements: { 
          point: {
            radius: 0,
            hitRadius: 10, 
            hoverRadius: 3
            } 
      }, 
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: false,
            display: false,
            },
          gridLines: {
              display: false,
          }
          }],
        xAxes: [{

        }]
      }
    },
  });

}


$("#search-form").on("submit", processForm)

