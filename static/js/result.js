$(document).ready(function() {

	$('form').on('submit', function(event) {
	    if (event.currentTarget.name) {
	        console.log();
	    }
		$.ajax({
			data : {
				name : event.currentTarget.name,
			},
			type : 'POST',
			url : '/result'
		})
		.done(function(data) {


			if (data.send) {
				$('#nsubm').show();
				$('#subm').hide();
			}

		});

		event.preventDefault();

	});

});