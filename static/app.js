function processForm(evt) {
  evt.preventDefault()
  const symbol = {
    ticker: $("symbol").val()
  }

  axios.post("/api/search", symbol)
  .then(function(response) {
    console.log(response) 
    processResponse(response)
  })
  .catch(function(error) {
    console.log(error)
  })
}

function processResponse(resp) {
  for (let data in resp.data) {
     const li = document.createElement('li');
     li.val() = data;
     $("#ticker").append(li);
  }
}


$("#ticker-search").on("submit", processForm);