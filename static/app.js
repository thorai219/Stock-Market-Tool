$(() => {
  axios.get("/index")
  .then((res) => {
    renderDowChart(res)
    renderNasdaqChart(res)
    renderSNPChart(res)
  })
  .catch((err) => console.log(err))

  axios.get("/movers")
  .then((res) => renderMovers(res))
  .catch((err) => console.log(err))

  $("#search-term").autocomplete({
    source: (request, response) => {
        $.getJSON("/api/auto/search",{
            q: request.term,
        }, function(data) {
            response(data.matching_results);
        });
    },
    minLength: 1,
  });

})

function processForm(e) {
  e.preventDefault();
  const userInput = {
    name: $("#search-term").val()
  }
  $("#search-term").val("")

  $("#chart").html(`
    <div class="chart-div">
      <canvas style="border: 1px solid black;" id="main-chart"></canvas>
    </div>
    <div id="main-info"></div>
    <div class="news"></div>
  `)

  axios.post("/search/company", userInput)
  .then((res) => renderChart(res))
  .catch((err) => console.log(err))
}

function determineLineColor(data) {
  let idx = data.length - 1;
  
  if (data[0] < data[idx]) {
    return '#008000'
  } else {
    return '#f70d1a'
  }
}

var index_chart_options = {
  elements: {
    point:{
        radius: 0
    },
    line: {
      tension: 0
    }
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
        display: true
      },
      ticks: {
        display: true
      }
    }]
  }
}

function renderSNPChart(res) {
  let data = res.data.snp;
  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    chart_date.unshift(item.date)
    chart_price.unshift(item.price)
  })

  new Chart(document.getElementById("snp-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "S&P 500",
          fill: false,
          borderWidth: 2,
          borderColor: determineLineColor(chart_price)
        }
      ]
    },
    options: index_chart_options
  });
}

function renderDowChart(res) {
  let data = res.data.dow;

  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    chart_date.unshift(item.date)
    chart_price.unshift(item.price)
  })

  new Chart(document.getElementById("dow-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "DOW",
          fill: false,
          borderWidth: 2,
          borderColor: determineLineColor(chart_price)
      
      }]
    },
    options: index_chart_options
  });
}


function renderNasdaqChart(res) {
  let data = res.data.nasdaq;
  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    chart_date.unshift(item.date)
    chart_price.unshift(item.price)
  })

  new Chart(document.getElementById("nasdaq-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "NASDAQ",
          fill: false,
          borderWidth: 2,
          borderColor: determineLineColor(chart_price)
      }]
    },
    options: index_chart_options
  });
}


function renderChart(res) {
  let data = res.data.chart;

  let chart_date = [];
  let chart_price = [];

  let symbol = res.data.news[0].symbol;

  $("#main-info").append(`
    <form action="/add/following/${symbol}">
      <button>Follow</button>
    </form>
  `)

  data.forEach((item) => {
    chart_date.unshift(item.date.slice(10,16));
    chart_price.unshift(item.price);
  })

  let news = res.data.news;

  news.forEach((item) => {
    $(".news").append(
      `
      <div class="card mt-2">
        <div class="row">
          <div class="col-sm-4">
            <img src="${item.image}" class="img-fluid">
          </div>
          <div class="col-sm-8" id="desc-card">
            <h4>${item.title}</h4>
            <p>${item.text}</p>
            <input style="width: 150px;" type="button" value="Read More..." onclick="window.open('${item.url}')" />
          </div>
        </div>
      </div>
      `
    )
  })


  var ctx = document.getElementById("main-chart");

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: symbol,
          fill: false,
          borderWidth: 2,
          borderColor: determineLineColor(chart_price)
        }
      ]
    },
    options: {
      responsive: true,
      gridLines: {
        color: "black"
      },
      elements: {
        point:{
            radius: 1
        },
        line: {
          tension: 0
        }
      },
      scales: {
        xAxes: [{
          display: true,
          gridLines: {
            display: false
          },
          ticks: {
            display: true
          }
        }],
        yAxes: [{
          display: true,
          gridLines: {
            display: true
          },
          ticks: {
            display: true
          }
        }]
      }
    }
  });
}


function renderMovers(res) {
  let data = res.data
  data.forEach((item) => {
    if (item.companyName !== null) {
      if (item.changesPercentage.indexOf("-") === -1) {
        $(".marquee-content").append(
          `
          <li style="color: #008000; font-size: 12px;">${item.ticker}<br>${item.changesPercentage}</li>
          `
        )
      } else {
        $(".marquee-content").append(
          `
          <li style="color: #ce1127; font-size: 12px;">${item.ticker}<br>${item.changesPercentage}</li>
          `
        )
      }  
    }
  })
}

function get_stock(query) {

  let symbol = {
    symbol: query
  }

  axios.post("/get/stock", symbol)
  .then((res) => {

    $("#chart").html(`
    <div class="chart-div">
      <canvas style="border: 1px solid black;" id="main-chart"></canvas>
    </div>
    <div id="main-info"></div>
    <div class="news"></div>
    `)

    renderChart(res)

  })
  .catch((err) => console.log(err))
}

$("#search-form").on("submit", processForm)