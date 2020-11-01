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
