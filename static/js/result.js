$(document).ready(function() {

	$('form').on('submit', function(event) {
		$.ajax({
			data : {
				id : event.currentTarget.name,
			},
			type : 'POST',
			url : '/result'
		})
		.done(function(data) {


			if (data.send) {
			    var names =  document.querySelectorAll('#add' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='none';
                }
                var names =  document.querySelectorAll('#add4' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='none';
                }
                var names =  document.querySelectorAll('#added' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='inline';
                }
			}
			if (data.notsend) {
			    var names =  document.querySelectorAll('#add' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='inline';
                }
                var names =  document.querySelectorAll('#added' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='none';

                }
                var names =  document.querySelectorAll('#add4d' + event.currentTarget.name);
			    for (let i = 0; i < names.length; i++) {
                    names[i].style.display='none';

                }
			}

		});

		event.preventDefault();

	});

});