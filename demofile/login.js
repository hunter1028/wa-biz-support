    $(document).ready(function(){
                // on click Sign In Button checks that username =='admin' and password == 'password'
                $("#loginButton").click(function(){
                if( $("#loginusername").val()=='admin' && $("#loginpassword").val()=='password') {
                        $("#first").hide();
                        $("#second").append("<p>Hello, admin</p> <br/><input type='button' id='logout' value='Log Out' />");
                    }
                else {
                    alert("Please try again");
                }

                $("#logout").click(function() {
                $("form")[0].reset();
                $("#first").show();
                $("#second").hide();
            });
        });

    });