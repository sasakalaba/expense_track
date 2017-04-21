$(document).ready(function() {
    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:8000/api/users/sasa/expenses/",
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', 'Token 4213ac8ac2e19eae2d0a599a58abde4b56a0fca8');
        },
        success: function(data) {
            var dtConf = {
                destroy: true,
                rowId: 'id',
                columns: [
                    {
                        'data': 'date',
                    },
                    {
                        'data': 'time',
                    },
                    {
                        'data': 'amount',
                    },
                    {
                        'data': 'comment',
                    },
                    {
                        'data': 'description',
                    },
                ],
                data: data,
                order: [[0, 'asc'], [1, 'asc']]
           };
           var dt = $('#dataTables-example_wrapper table').DataTable(dtConf);
        }
    });

    $(document).ajaxSend(function(event, xhr) {
       function getCookie(name) {
           var cookieValue = null;
           if (document.cookie && document.cookie !== '') {
               var cookies = document.cookie.split(';');
               for (var i = 0; i < cookies.length; i++) {
                   var cookie = cookies[i].trim();
                   if (cookie.substring(0, name.length + 1) == (name + '=')) {
                       cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                       break;
                   }
               }
           }
           return cookieValue;
       }

       xhr.withCredentials = true;

       xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
   });


})

/*
$.ajax({
    url: "url",
    type: "POST",
    data: {a: "value", b: "value2", csrftoken: ""}
}).done(function(data) {

}).fail(function(jqXHR) {
    console.log(jqXHR)
})

var redak = "<tr><td class='klasa'>" + varijabla + "</td></tr>"
$("#moja-tablica tbody").append(redak)
*/
