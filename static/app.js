function getNewsArticle(evt) {
  evt.preventDefault()
  const symbol = {
    company: $("search-company").val()
  }

  axios.post("/api/search/company/news", symbol)
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


$("#search-news").on("submit", getNewsArticle);