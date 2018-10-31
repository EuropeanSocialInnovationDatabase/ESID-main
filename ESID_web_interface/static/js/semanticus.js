var mainAddress = window.location.origin+'/';

function loginRedirect(response) {
        var token = response;

        console.log("cookies set");
        $("#Logout-link").css("visibility", "visible");
        // Check if user is admin
        $.ajax({
            type: "POST",
            url: mainAddress + "is_admin",
            data: JSON.stringify({
                user: Cookies.get("username"),
                token: token
            }),
            contentType: "application/json; charset=utf-8",
            success: function(responseAdmin) {
                if (String(responseAdmin) === "Yes") {
                    window.location.replace(mainAddress + "admin_dash");
                } else {
                    window.location.replace(mainAddress + "home");
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
$("#wrong_password").hide();
$("#user_exists").hide();
$("#password_match").hide();
$("#valid_email").hide();
$("#submit_registration").click(function() {
    var username = $("#username").val();
    var first_name = $("#first_name").val();
    var last_name = $("#last_name").val();
    var password = $("#password").val();
    var password2 = $("#password2").val();
    var city = $("#city").val();
    var institution = $("#institution").val();
    var country = $("#country").val();
    var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (re.test(username) === false) {
        $("#valid_email").show();
        return;
    }

    if (password.length <= 6 || password!=password2) {
        $("#password_match").show();
        return;
    }

    payload = {
        user: username,
        first_n : first_name,
        last_n: last_name,
        pass: password,
        organization: institution,
        city: city,
        country: country
    };

    $.ajax({
        type: "POST",
        url: mainAddress + "register",
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
            console.log("success");

            if (String(response) === "Successfully created user") {

                Cookies.set("username", username);
                console.log("cookies set");

                $.ajax({
                    type: "POST",
                    url: mainAddress + "get_token",
                    data: JSON.stringify({
                        user: username,
                        pass: password
                    }),
                    contentType: "application/json; charset=utf-8",
                    success: function(responseToken) {
                        console.log("success");
                        Cookies.set("username", username);
                        Cookies.set("token", responseToken);
                        Cookies.set("newUser", "True");
                        console.log("cookies set");
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            window.location.replace(mainAddress + "user_created");
            } else {
                $("#user_exists").show();
            }
        },
        error: function(error) {
            console.log(error);
        }
    });
});


$("#submit_login").click(function() {
    var username = $("#username").val();
    var password = $("#password").val();

    payload = {
        user: username,
        pass: password,
    };

    $.ajax({
        type: "POST",
        url: mainAddress + "get_token",
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
            console.log("success");
            if("ERROR: User does not exist" == response)
            {
                $("#wrong_password").show();
                return;
            }
                Cookies.set("username", username);
                Cookies.set("token", response);
                            loginRedirect(response);
                        }
                        ,
                        error: function(error) {
                        console.log(error);
                        }
            });
        });
$('#Logout').click(function() {
    username = Cookies.get("username");
    tokenA = Cookies.get("token");
    payload = {
        user: username,
        token: tokenA,
    };
     $.ajax({
        type: "POST",
        url: mainAddress + "logout",
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
            console.log("success");
            window.location.replace(mainAddress+'/');

                        }
                        ,
        error: function(error) {
            console.log(error);
                        }
            });
});

function userLoggedIn() {
    $.ajax({
        type: "POST",
        url: mainAddress + "is_logged",
        data: JSON.stringify({
            user: Cookies.get("username"),
            token: Cookies.get("token")
        }),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
            if (response !== "Yes") {
                console.log("User is not logged in");
                window.location.replace(mainAddress);
            }
        },
        error: function(error) {
            window.location.replace(mainAddress);
            console.log(error);
        }
    });
}

$('#classify').click(function() {
textA = $("#text_to_process").val();
url_page = "classify_text"
SendData(textA,url_page)
});

function SendData(textA,url_page){
$.ajax({
        type: "POST",
        url: mainAddress + url_page,
        data: JSON.stringify({
            user: Cookies.get("username"),
            token: Cookies.get("token"),
            text: textA
        }),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
        if ("User not logged in" === response){
            window.location.replace(mainAddress);
            }
        $('#output').html("Hello Word2")

        },
        error: function(error) {
            console.log(error);
        }
    });

}

var counter = 0;

$("#add_actor").click(function() {
$("#actors").append("<label for='actor_name_"+counter+"'>Actor Name: </label><input name='actor_name_"+counter+"' value='' type='text'/><br/>");
$("#actors").append("<label for='actor_website_"+counter+"'>Actor Website: </label><input name='actor_website_"+counter+"' value='' type='text'/><br/>");
$("#actors").append("<label for='actor_city_"+counter+"'>Actor City: </label><input name='actor_city_"+counter+"' value='' type='text'/><br/>");
$("#actors").append("<label for='actor_country_"+counter+"'>Actor Country: </label><input name='actor_country_"+counter+"' value='' type='text'/><br/>");
$("#counter").val(counter + 1);
counter = counter + 1;
});


function userLoggedIn() {
    $.ajax({
        type: "POST",
        url: mainAddress + "is_logged",
        data: JSON.stringify({
            user: Cookies.get("username"),
            token: Cookies.get("token")
        }),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
            if (response !== "Yes") {
                console.log("User is not logged in");
                window.location.replace(mainAddress);
            }
        },
        error: function(error) {
            window.location.replace(mainAddress);
            console.log(error);
        }
    });
}