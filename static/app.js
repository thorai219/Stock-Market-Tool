$(() => {
  $("#search").autocomplete({
    source: (request, response) => {
        $.getJSON("/search",{
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
    name: $("#search").val()
  }

  axios.post("/search/company", userInput)
  .then((res) => renderChart(res))
  .catch((err) => console.log(err))
}

let chart_options = {
  elements: {
    point:{
        radius: 0
    },
    line: {
      tension: 0
    }
  },
  chartArea: {
      backgroundColor: 'rgb(0, 0, 0)'
  },
  scales: {
    xAxes: [{
      display: false,
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
        display: true
      }
    }]
  }
}

function renderChart(res) {
  renderPress(res);
  renderProfile(res);

  let data = res.data.chart;

  let chart_date = [];
  let chart_price = [];

  let symbol = res.data.news[0].symbol;

  data.forEach((item) => {
    chart_date.unshift(item.date.slice(10,16));
    chart_price.unshift(item.price);
  })

  let ctx = document.getElementById("chart").getContext("2d");

  var gradientFill = ctx.createLinearGradient(0, 0, 0, 380);
  gradientFill.addColorStop(0, "black");
  gradientFill.addColorStop(1, "white"); 

  var stockChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chart_date,
      datasets: [{ 
          data: chart_price,
          label: symbol,
          fill: true,
          borderWidth: 1,
          backgroundColor: gradientFill,
          borderColor: "black",
          hoverRadius: 5
        }
      ]
    },
    options: chart_options
  });
}

function renderPress(res) {
  let press = res.data.press;

  press.forEach((item) => {
    $(`.news-container`).append(`
      <div class="press">
        <h4>${item.title}</h4>
        <p>${item.text}</p>
      </div>
    `)
  })
}

function renderProfile(res) {
  let company = res.data.profile[0];

  $(".info").append(`
    <div>
      <h3>${company.companyName}</h3>
      <p>${company.description}</p>
      <form action="/add/following/${company.symbol}">
        <button class="follow-btn">Follow</button>
      </form>
    </div>
  `)

  $(".options").append(`
    <div>
      <button onclick="todays_chart">Daily</button>
    </div>
    <div class="weekly">
      <button class="${company.symbol}">Weekly</button>
    </div>
    <div>
      <button onclick="monthly_chart">Monthly</button>
    </div>
  `)
}

$("#search-form").on("submit", processForm)