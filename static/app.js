var SEARCHTERM = {}

$(() => {
  axios.get("/get/ticker/sector")
  .then((res) => renderSector(res))
  .catch((err) => console.log(err)) 

  axios.get("/get/index/snp")
  .then((res) => renderSNPChart(res))
  .catch((err) => console.log(err))

  axios.get("/get/index/dow")
  .then((res) => renderDowChart(res))
  .catch((err) => console.log(err))

  axios.get("/get/index/nasdaq")
  .then((res) => renderNasdaqChart(res))
  .catch((err) => console.log(err))

  $("#search-field").autocomplete({
    source:function(request, response) {
        $.getJSON("/api/auto/search",{
            q: request.term,
        }, function(data) {
            response(data.matching_results);
        });
    },
    minLength: 2,
    select: function(event, ui) {
      SEARCHTERM.name = ui.item.value;
    }
  });
})

function renderSector(res) {
  let data = res.data;
  data.forEach((item) => {
    if (item.changesPercentage.indexOf("-") === -1) {
      $("#sector-deck").append(
        `<div class="card">
          <div class="card-body">
            <p class="card-text" style="color: #00ff00; font-size: 12px;">${item.sector}<br>${item.changesPercentage}</p>
          </div>  
        </div>`
      )
    } else {
      $("#sector-deck").append(
        `<div class="card">
          <div class="card-body">
            <p class="card-text" style="color: #e50000; font-size: 12px;">${item.sector}<br>${item.changesPercentage}</p>
          </div>  
        </div>`
      )
    }
  })
}

function renderSNPChart(res) {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0');
  var yyyy = today.getFullYear();

  today = `${yyyy}-${mm}-${dd}`;
  let data = res.data;

  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    let date = item.date.slice(0,10);
    if (date === today) {
      chart_date.push(item.date)
      chart_price.push(item.close)
    }
  })

  new Chart(document.getElementById("snp-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "S&P 500",
          fill: false
        }
      ]
    },
    options: {
      gridLines: {
        color: "#ce1127"
      },
      scales: {
        xAxes: [{
          display: true,
          gridLines: {
            display: false
          },
          ticks: {
            display: false
          }
        }],
        yAxes: [{
          display: true,
          gridLines: {
            display: false
          },
          ticks: {
            display: false
          }
        }]
      }
    }
  });
}


function renderDowChart(res) {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0');
  var yyyy = today.getFullYear();

  today = `${yyyy}-${mm}-${dd}`;
  let data = res.data;

  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    let date = item.date.slice(0,10);
    if (date === today) {
      chart_date.push(item.date)
      chart_price.push(item.close)
    }
  })

  new Chart(document.getElementById("dow-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "DOW",
          fill: false
        }
      ]
    },
    options: {
      gridLines: {
        color: "#ce1127"
      },
      scales: {
        xAxes: [{
          display: true,
          gridLines: {
            display: false
          },
          ticks: {
            display: false
          }
        }],
        yAxes: [{
          display: true,
          gridLines: {
            display: false
          },
          ticks: {
            display: false
          }
        }]
      }
    }
  });
}


function renderNasdaqChart(res) {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0');
  var yyyy = today.getFullYear();

  today = `${yyyy}-${mm}-${dd}`;
  let data = res.data;
  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    let date = item.date.slice(0,10);
    if (date === today) {
      chart_date.push(item.date)
      chart_price.push(item.close)
    }
  })

  new Chart(document.getElementById("nasdaq-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "NASDAQ",
          fill: false
        }
      ]
    },
    options: {
      gridLines: {
        color: "#ce1127"
      },
      scales: {
        xAxes: [{
          display: true,
          gridLines: {
            display: true
          },
          ticks: {
            display: false
          }
        }],
        yAxes: [{
          display: true,
          gridLines: {
            display: true
          },
          ticks: {
            display: false
          }
        }]
      }
    }
  });
}

function renderChart(evt) {
  evt.preventDefault();

  axios.get("/api/get/chart")
  .then((res) => console.log(res))
  .catch((err) => console.log(err))

}



$("#search-form").on("submit", renderChart)


