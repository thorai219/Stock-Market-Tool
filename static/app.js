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

  axios.get("/get/get/movers")
  .then((res) => renderMovers(res))
  .catch((err) => console.log(err))

  axios.get("/get/headlines")
  .then((res) => renderNews(res))
  .catch((err) => console.log(err))


  $("#search-field").autocomplete({
    source: (request, response) => {
        $.getJSON("/api/auto/search",{
            q: request.term,
        }, function(data) {
            response(data.matching_results);
        });
    },
    minLength: 2,
  });
})

function renderSector(res) {
  let data = res.data;
  data.forEach((item) => {
    if (item.changesPercentage.indexOf("-") === -1) {
      $("#sector-deck").append(
        `<div class="card">
          <div class="card-body">
            <p class="card-text" style="color: #009a00; font-size: 12px;">${item.sector}<br>${item.changesPercentage}</p>
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
      chart_date.unshift(item.date)
      chart_price.unshift(item.close)
    }
  })

  new Chart(document.getElementById("snp-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "S&P 500",
          fill: true,
          borderWidth: 1,
          borderColor: "#000000"
        }
      ]
    },
    options: {
      gridLines: {
        color: "#ce1127"
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
      chart_date.unshift(item.date)
      chart_price.unshift(item.close)
    }
  })

  new Chart(document.getElementById("dow-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "DOW",
          fill: true,
          borderWidth: 1,
          borderColor: "#000000"
      
      }]
    },
    options: {
      gridLines: {
        color: "#ce1127"
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
      chart_date.unshift(item.date)
      chart_price.unshift(item.close)
    }
  })

  new Chart(document.getElementById("nasdaq-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: "NASDAQ",
          fill: true,
          borderWidth: 1,
          borderColor: "#000000"
      }]
    },
    options: {
      gridLines: {
        color: "#ce1127"
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

function renderMovers(res) {
  let data = res.data
  data.actives.forEach((item) => {
    if (item.companyName !== null) {
      if (item.changesPercentage.indexOf("-") === -1) {
        $("#actives").append(
          `
          <li style="color: #009a00; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      } else {
        $("#actives").append(
          `
          <li style="color: #ce1127; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      }  
    }
  })
  data.gainers.forEach((item) => {
    if (item.companyName !== null) {
      if (item.changesPercentage.indexOf("-") === -1) {
        $("#gainers").append(
          `
          <li style="color: #009a00; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      } else {
        $("#gainers").append(
          `
          <li style="color: #ce1127; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      }  
    }
  })
  data.losers.forEach((item) => {
    if (item.companyName !== null) {
      if (item.changesPercentage.indexOf("-") === -1) {
        $("#losers").append(
          `
          <li style="color: #009a00; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      } else {
        $("#losers").append(
          `
          <li style="color: #ce1127; font-size: 12px;">${item.companyName} ${item.changesPercentage}</li>
          `
        )
      }  
    }
  })
}

function renderNews(res) {
  let data = res.data;
  console.log(data)
  data.articles.forEach((item) => {
    $("#main-news").append(
      `
      <div class="card deck">
        <div class="row">
          <div class="col-sm-4">
            <img src="${item.urlToImage}" class="img-fluid">
          </div>
          <div class="col-sm-8" id="desc-card">
            <h4>${item.title}</h4>
            <p>${item.description}</p>
            <input type="button" value="Read More..." onclick="window.open('${item.url}')" />
          </div>
        </div>
      </div>
      `
    )
  })
}

function getChartInfo(evt) {
  evt.preventDefault();
  const userInputs ={
    name: $("#search-field").val()
  }

  $("#search-field").val("")
  $("#main-news").html(`
  <div class="container">
    <div id="company-name"></div>
    <div class="row">
      <div class="col-sm-8" id="chart-div">
        <canvas class="deck" id="main-chart"height="200"></canvas>
      </div>
      <div class="col-sm-4" id="company-info">

      </div>
    </div>
    <div id="company-news"></div>
  </div>
  `)
  $("#company-name").html("")
  $("#company-info").html("")
  $("#chart-div").html("<canvas id='main-chart' height='200'></canvas>")


  axios.post("/api/get/chart", userInputs)
  .then((res) => {
    renderChart(res)
    renderInfo(res)
  })
  .catch((err) => console.log(err))

  axios.post("/api/get/news", userInputs)
  .then((res) => {
    renderCompanyNews(res)

  })
  .catch((err) => console.log(err))
}

function renderChart(res) {
  let data = res.data.chart;
  let chart_date = [];
  let chart_price = [];

  data.forEach((item) => {
    chart_date.unshift(item.date);
    chart_price.unshift(item.price);
  })

  let userInput = $("#search-field").val();

  new Chart(document.getElementById("main-chart"), {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: userInput,
          fill: true,
          borderWidth: 1,
          borderColor: "#000000"
        }
      ]
    },
    options: {
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

function renderInfo(res) {
  let data = res.data.company[0];
  console.log(data)
  $("#company-name").append(
    `
    <h3 class="text-center">${data.companyName}</h3>
    `
  )
  $("#company-info").append(
    `
    <div class="card text-center" style="width: 18rem; height: 200px;">
    <ul class="list-group list-group-flush">
      <li class="list-group-item"><img src="${data.image}"></li>
      <li class="list-group-item">CEO: ${data.ceo}</li>
      <li class="list-group-item">Symbol: ${data.symbol}</li>
      <li class="list-group-item">Exchange: ${data.exchangeShortName}</li>
      <li class="list-group-item">Sector: ${data.sector}</li>
      <li class="list-group-item">Industry: ${data.industry}</li>
      <li class="list-group-item">Price: $${data.price}</li>
      <li class="list-group-item">Changes: ${data.changes}</li>
    </ul>
  </div>
    `
  )
}

function renderCompanyNews(res) {
  let data = res.data.articles;
  console.log(data)
  data.forEach((item) => {
    $("#company-news").append(`
      <div class="card deck">
        <div class="row">
          <div class="col-sm-4">
            <img src="${item.urlToImage}" class="img-fluid">
          </div>
          <div class="col-sm-8" id="desc-card">
            <h4>${item.title}</h4>
            <p>${item.description}</p>
            <input type="button" value="Read More..." onclick="window.open('${item.url}')" />
          </div>
        </div>
      </div>
    `)
  })
}


$("#search-form").on("submit", getChartInfo)


