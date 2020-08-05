function processForm(evt) {
  evt.preventDefault()
  const symbols = {
    symbol : $("symbol").val()
  }

  axios.post("/api/search", symbols)
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
    
  }
  $("#ticker").html(resp.data)
}


$("#ticker-search").on("submit", processForm);