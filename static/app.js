$(() => {
  $("#search").autocomplete({
    source: (request, response) => {
      $.getJSON(
        "/search",
        {
          q: request.term,
        },
        function (data) {
          response(data.matching_results);
        }
      );
    },
    minLength: 1,
  });
});

$("#search-form").on("submit", async function (e) {
  e.preventDefault();
  let name = $("#search").val();

  const search = {
    value: name,
  };

  $("#chart").html("");
  $("#chart").append(`
    <div class='container'>
      <div class='card mt-4'>
        <div class='card-header'></div>
        <div class="chart-container card-body">
          <canvas id="myChart" class="myChart"></canvas>
        </div>
      </div>
      <div id='profile'></div>
    </div>
  `);

  const chart = await axios.post("/search/ticker", search);
  const profile = await axios.post("/get/profile", search);

  renderCompanyProfile(profile);
  renderChart(chart);
});

const options = {
  tooltips: {
    mode: "interpolate",
    intersect: false,
  },
  plugins: {
    crosshair: {
      line: {
        color: "#000000",
        width: 1,
      },
      sync: {
        enabled: false,
      },
      zoom: {
        enabled: false,
      },
      callbacks: {
        beforeZoom: function (start, end) {
          return true;
        },
        afterZoom: function (start, end) {},
      },
    },
  },
  responsive: true,
  maintainAspectRatio: false,
  legend: {
    display: false,
  },
  elements: {
    point: {
      radius: 0,
    },
    line: {
      tension: 0,
    },
  },
  chartArea: {
    backgroundColor: "rgb(0, 0, 0)",
  },
  scales: {
    xAxes: [
      {
        display: false,
        gridLines: {
          display: true,
        },
        ticks: {
          display: false,
        },
      },
    ],
    yAxes: [
      {
        display: true,
        position: "right",
        gridLines: {
          display: true,
        },
        ticks: {
          display: true,
        },
      },
    ],
  },
};

function color(arr) {
  if (arr[arr.length - 1] < arr[0]) {
    return "rgb(231,76,60)";
  }
  return "rgb(46,204,113)";
}

function shade(arr) {
  if (arr[arr.length - 1] < arr[0]) {
    return "rgba(231,76,60,0.3)";
  }
  return "rgba(46,204,113,0.3)";
}

function renderChart(result) {
  let labels = [];
  let prices = [];
  result.data.forEach((item) => {
    labels.unshift(item.date);
  });
  result.data.forEach((item) => {
    prices.unshift(item.close);
  });

  const ctx = $("#myChart");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          data: prices,
          fill: true,
          borderWidth: 2,
          backgroundColor: shade(prices),
          borderColor: color(prices),
        },
      ],
    },
    options: options,
  });
}

function renderCompanyProfile(profile) {
  let company = profile.data.company[0];
  let financials = profile.data.financial[0];
  let ratings = profile.data.rating;

  $(".card-header").append(`
    <div class="company-container">
      <div class="d-flex">
        <img src='${company.image}' class='mx-4 img-logo' />
        <h3 class='mx-4 text-center'>${company.companyName}<br />${company.symbol} - ${company.exchangeShortName}</h3>
      </div>
    </div>
  `);

  $("#profile").append(`
    <div class="card">
      <div class="card-body">
        <p>${company.description}</p>
      </div>
    </div>
  `);

  $("#profile").append(`
    <div class="card justify-content-around profile-tables">
      <div>
        <table class="table table-striped table-custom">
          <thead>
            <tr>
              <td>
                <h3>Profile</h3>
              </td>
            </tr>
          </thead>
          <tr>
            <td>CEO</td>
            <td>${company.ceo}</td>
          </tr>
          <tr>
            <td>Industry</td>
            <td>${company.industry}</td>
          </tr>
          <tr>
            <td>Sector</td>
            <td>${company.sector}</td>
          </tr>
          <tr>
            <td>Changes</td>
            <td>${company.changes}</td>
          </tr>
          <tr>
            <td>Volume AVG</td>
            <td>${company.volAvg}</td>
          </tr>
          <tr>
            <td>Market-Cap</td>
            <td>${company.mktCap}</td>
          </tr>
          <tr>
            <td>Last dividend</td>
            <td>${company.lastDiv}</td>
          </tr>
        </table>
      </div>

      <div>
        <table class="table table-striped table-custom">
          <thead>
            <tr>
              <td>
                <h3>Financials</h3>
              </td>
            </tr>
          </thead>
          <tr>
            <td>Date</td>
            <td>${financials.date}</td>
          </tr>
          <tr>
            <td>Revenue</td>
            <td>${financials.revenue}</td>
          </tr>
          <tr>
            <td>Cost of revenue</td>
            <td>${financials.costOfRevenue}</td>
          </tr>
          <tr>
            <td>Gross profit</td>
            <td>${financials.grossProfit}</td>
          </tr>
          <tr>
            <td>R&D expense</td>
            <td>${financials.researchAndDevelopmentExpenses}</td>
          </tr>
          <tr>
            <td>EBITDA</td>
            <td>${financials.ebitda}</td>
          </tr>
          <tr>
            <td>Earnings per share</td>
            <td>${financials.eps}</td>
          </tr>
        </table>
      </div>

      <div>
        <table class="table table-striped table-custom">
          <thead>
            <tr>
              <td>
                <h3>Ratings</h3>
              </td>
            </tr>
          </thead>
          <tbody id="ratings">
          </tbody>
        </table>
      </div>

    </div>

  `);

  ratings.forEach((rate) => {
    $("#ratings").append(`
      <tr>
        <td>${rate.gradingCompany}</td>
        <td>${rate.newGrade}</td>
      </tr>
    `);
  });
}
