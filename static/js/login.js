$(document).ready(function() {

	$('#login').on('submit', function(event) {

		$.ajax({
			data : {
				login : $('#floatingInput').val(),
				password : $('#floatingPassword').val(),
				code : $('#floatingCode').val()
			},
			type : 'POST',
			url : '/login'
		})
		.done(function(data) {

			if (data.code) {
				$('#alert').show();
				$('#alert').show();
				$('#code').show();
				$('#log').hide();
				$('#password').hide();
			}
			if (data.login) {
			    window.location.href = "/";
			}
			if (data.index) {
			    window.location.href = "/";
			}
			if (data.error) {
			    $('#errAlert').text(data.error).show();
			}
		});

		event.preventDefault();

	});

});