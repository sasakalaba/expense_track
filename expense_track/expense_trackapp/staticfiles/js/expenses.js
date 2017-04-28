$(document).ready(function() {
	getTable();
});

function getTable() {
	if (window.dt) {
		window.dt.destroy();
		$('#expenses-table tbody').html('');
	}
	var token = 'Token ' + window.token;
	var username = window.user;
	var url = '/api/users/' + username + '/expenses/';
	$.ajax({
        url: url,
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', token);
        },
        success: function(data) {
        	window.data = data;
        	$.each(data, function(i, val) {
        		var row = '<tr><td>';
        		row += val.date + '</td><td>' + val.time + '</td><td>';
        		row += val.amount + '</td><td>' + val.comment + '</td><td>';
        		row += val.description + '</td><td>';
        		row += '<button class="btn btn-success edit" id="' + val.pk + '">Edit</button></td><td>'
        		row += '<button class="btn btn-danger delete" id="' + val.pk + '">Delete</button></td>'
        		row += '</tr>';
        		$('#expenses-table tbody').append(row);
        	});
            var dtConf = {
                destroy: true,
                order: [[0, 'asc'], [1, 'asc']],
                responsive: true,
		        select: {
		            style:    'os',
		            selector: 'td:first-child'
		        }
           	};
           	window.dt = $('#expenses-table').DataTable(dtConf);
           	$('.delete').on('click', function() {
				var id = $(this).attr('id');
				deleteExpense(id);
		   	});
		   	$('.edit').on('click', function() {
				var id = $(this).attr('id');
				editExpense(id);
		   	});
        },
        error: function(jqXHR) {
        	console.log(jqXHR);
        }
    });
}

function deleteExpense(id) {
	var user, i, ok;
	ok = confirm('Are you sure you want to delete this expense?');
	if (!ok) return;
	for (i = 0; i < window.data.length; i += 1) {
		if (window.data[i].pk === parseInt(id)) {
			user = window.data[i].user;
			break;
		}
	}
	if (!user) return;
	var url = '/api/users/' + user + '/expenses/' + id;
	var token = 'Token ' + window.token;
	$.ajax({
		url: url,
		type: 'DELETE',
	 	beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', token);
        },
        data: { csrftoken: Cookies.get('csrftoken') },
        success: getTable,
        error: function(jqXHR) {
        	console.log(jqXHR);
        }
	});
}

function editExpense(id) {
	var expense, i;
	for (i = 0; i < window.data.length; i += 1) {
		if (window.data[i].pk === parseInt(id)) {
			expense = window.data[i];
			break;
		}
	}
	if (!expense) return;

	$('#mform-user').val(expense.user);
	$('#mform-date').val(expense.date);
	$('#mform-time').val(expense.time);
	$('#mform-amount').val(expense.amount);
	$('#mform-description').val(expense.description);
	$('#mform-comment').val(expense.comment);
	$('#mform-id').val(expense.pk);
	$('#edit-modal').modal();
}

$('#msave').click(function() {
	var amount = $('#mform-amount').val();
	if (!amount) {
		alert('Amount is required!');
		return;
	}
	var user = $('#mform-user').val();
	var date = $('#mform-date').val();
	var time = $('#mform-time').val();
	var description = $('#mform-description').val();
	var comment = $('#mform-comment').val();
	var id = $('#mform-id').val();

	var url = '/api/users/' + user + '/expenses/' + id;
	var token = 'Token ' + window.token;
	$.ajax({
		url: url,
		type: 'PUT',
	 	beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', token);
        },
        data: {
        	csrftoken: Cookies.get('csrftoken'),
        	id: id,
        	amount: amount,
        	date: date,
        	time: time,
        	description: description,
        	comment: comment
        },
        success: function(data) {
        	getTable()
        	$('#edit-modal').modal('toggle');
        },
        error: function(jqXHR) {
        	console.log(jqXHR);
        }
	});
});

$('#add-expense').click(function() {
	$(this).hide();
	$('#new-expense').show();
});

$('#cancel').click(function() {
	$('#new-expense').hide();
	$('#add-expense').show();
});

$('#new-expense').submit(function(e) {
	e.preventDefault();
	var amount = $('#form-amount').val();
	if (!amount) {
		alert('Amount is required!');
		return;
	}
	var date = $('#form-date').val();
	var time = $('#form-time').val();
	var description = $('mform-description').val();
	var comment = $('#form-comment').val();

	var url = '/api/users/' + window.user + '/expenses/';
	var token = 'Token ' + window.token;
	$.ajax({
		url: url,
		type: 'POST',
	 	beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', token);
        },
        data: {
        	csrftoken: Cookies.get('csrftoken'),
        	amount: amount,
        	date: date,
        	time: time,
        	description: description,
        	comment: comment
        },
        success: function(data) {
        	getTable();
        	$('#new-expense').hide();
			$('#add-expense').show();
			$('#new-expense').find(
				"input[type=text], input[type=number], input[type=Date], input[type=Time]"
				).val("");
        },
        error: function(jqXHR) {
        	console.log(jqXHR);
        }
	});
});
