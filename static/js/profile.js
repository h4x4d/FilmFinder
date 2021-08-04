$(document).ready(function() {

    $('form').on('submit', function(event) {

        $.ajax({
            data: {
                name : $('#nameInput').val(),
                email : $('#floatingPassword').val()
            },
            type : 'POST',
            url : '/process'

        });
        .done(function(data) {

            if (data.error) {
                $('#sendAlert').show();

            }
            else {
                $('#sendAlert').show();
            }


        });

        event.preventDefault();


    });

});