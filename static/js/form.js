$(document).ready(function() {

	$('#2fa').on('submit', function(event) {

		$.ajax({
			data : {
				username : $('#userInput').val(),
				pass : $('#passInput').val()
			},
			type : 'POST',
			url : '/process'
		})
		.done(function(data) {

			if (data.send) {
				$('#successAlert').show();
				$('#errorAlert').hide();
			}
			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}

		});

		event.preventDefault();

	});

});
$(document).ready(function() {

    $('#changepass').on('submit', function(event) {

		$.ajax({
			data : {
				oldpass : $('#oldpass').val(),
				pass : $('#newpass').val(),
				pass_2 : $('#newpass-2').val(),
				code : $('#code-auth').val()
			},
			type : 'POST',
			url : '/passchange'
		})
		.done(function(data) {

			if (data.alert) {
				$('#sucAlert').show();
				$('#succAlert').hide();
				$('#errAlert').hide();
				$('#fir-pass').hide();
				$('#sec-pass').hide();
				$('#thr-pass').hide();
				$('#auth-code').show();
			}
			if (data.error) {
			    $('#succAlert').hide();
				$('#errAlert').text(data.error).show();
				$('#sucAlert').hide();
			}
			if (data.success) {
			    $('#errAlert').hide();
			    $('#sucAlert').hide();
			    $('#auth-code').hide();
				$('#succAlert').text(data.success).show();
				$('#subm-pass').hide();
			}

		});

		event.preventDefault();

	});

});
$(document).ready(function() {

	$('#clearhsitory').on('submit', function(event) {

		$.ajax({
			data : {
				type : 'clearhistory'
			},
			type : 'POST',
			url : '/profile_act'
		})
		.done(function(data) {

			if (data.delete) {
			    $('#erroAlert').text(data.delete).show();
			}

		});

		event.preventDefault();

	});

});
$(document).ready(function() {

	$('#clearliked').on('submit', function(event) {

		$.ajax({
			data : {
				type : 'clearliked'
			},
			type : 'POST',
			url : '/profile_act'
		})
		.done(function(data) {

			if (data.delete) {
			    $('#erroAlert').text(data.delete).show();
			}

		});

		event.preventDefault();

	});

});
$(document).ready(function() {

	$('#exit').on('submit', function(event) {

		$.ajax({
			data : {
				type : 'exit'
			},
			type : 'POST',
			url : '/profile_act'
		})
		.done(function(data) {

			if (data.delete) {
			    window.location.href = "/login";
			}

		});

		event.preventDefault();

	});

});