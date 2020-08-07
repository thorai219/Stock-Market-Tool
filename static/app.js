function processForm(evt) {
  evt.preventDefault();

  const userInputs = { 
    name: $("#term").val()
  }
  console.log(userInputs)
  axios.post('/api/search/company/news', userInputs)
  .then(function (response) {
    console.log(response)
    processResponse(response)
  })
  .catch(function (error) {
    console.log(error)
  });
};

function processResponse(res) {
  const result = res.data
  $("#result").append(
    `<div class="card mb-3">
      <a href="${result.url}">
        <img src="${result.urlToImage}" class="card-img-top" alt="image for news">
        <div class="card-body">
          <h5 class="card-title">${result.title}</h5>
          <p class="card-text">${result.description}</p>
          <p class="card-text"><small class="text-muted">${result.publishedAt}</small></p>
        </div>
      </a>
    </div>`
  )
}



$("#search").on("submit", processForm)