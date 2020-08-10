function processForm(evt) {
  evt.preventDefault();

  const userInputs = { 
    name: $("#search-term").val()
  }
  console.log(userInputs)
  axios.post('/api/stock/chart', userInputs)
  .then(function (response) {
    makeChart(response)
  })
  .catch(function (error) {
    console.log(error)
  });
};

function makeChart(res) {
  const result = res.data
  var ctx = document.getElementById('chart').getContext('2d');

  let date = [];
  let price = [];
  
  try {
    result.map((item) => {
      date.push(item.date);
      price.push(item.price);
    });
  
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [...date],
        datasets: [{
          data: [...price],
          fill: false,
          borderColor: ['black'],
          borderWidth: 1.5
        }]
      },
      options: {
        maintainAspectRatio: false,
        elements: { 
            point: {
              radius: 0,
              hitRadius: 10, 
              hoverRadius: 3
              } 
            } 
          },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: false
            }
          }]
        }
      }
    );
  
  } catch (error) {
    console.log(error);
  }
}

// function processResponse(res) {
//   const result = res.data
//   $("#result").append(
//     `<div class="card mb-3">
//       <a href="${result.url}">
//         <img src="${result.urlToImage}" class="card-img-top" alt="image for news">
//         <div class="card-body">
//           <h5 class="card-title">${result.title}</h5>
//           <p class="card-text">${result.description}</p>
//           <p class="card-text"><small class="text-muted">${result.publishedAt}</small></p>
//         </div>
//       </a>
//     </div>`
//   )
// }



$("#search-form").on("submit", processForm)

