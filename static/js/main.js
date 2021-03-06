var url = "ws://" + location.host + "/tweetsocket";
var socket = new WebSocket(url);

var TWEET_LIMIT = 100;

var running = false;
var tweets = 0;

$(function() {
    $("#start").on("click", function(e)  {
        start(e);
    });

    $("#stop").on("click", function(e)  {
        stop(e);
    });

    $("#pause").on("click", function(e)  {
        pause_or_resume(e)
    });

    $('#query').on('keyup', function(e) {
        var length = $(this).val().length;
        if (length > 0) {
            $("#start").addClass('enabled').removeClass('disabled');
        } else {
            $("#start").addClass('disabled').removeClass('enabled');
        }
    });

    $('#query').on('keypress', function(e) {
        var code = e.keyCode || e.which;
        if(code == 13) { //Enter keycode
            $('#start').click();
        }
    });
});

socket.onopen = function() {
    console.log('open');
};
socket.onmessage = function(e) {
    data = JSON.parse(e.data);
    if (data.message === "newTweet") {
        newTweet(data.tweet);
    }
};
socket.onclose = function() {
    console.log('close');
};

function start(event) {
    if ($(event.target).hasClass('disabled')) return;
    // Unhide tweet section
    $('#screen2').show();

    // Scroll to it
    $("body").animate({
            scrollTop: $('#screen2').offset().top
        }, 600, "swing", function() {
            // Send Start event and set local variables
            running = true;
            var message = {
                message: "start",
                track: $("#query").val()
            };
            socket.send(JSON.stringify(message));

        // Hide & cleanup header section
        $("#screen1").hide(); 
        $("#query").val(""); 
        $("#start").addClass("disabled").removeClass("enabled");
    });
}

function stop(event) {
    $("#screen1").show();
    $("body").animate({
        scrollTop: $('#screen2').offset().top
    }, 0);
    $("body").animate({
        scrollTop: $("#screen1").offset().top
    }, 600, "swing", function() {
        $('#screen2').hide();
        $('#screen2_tweets').empty();

        // Reset pause button
        $('#pause').addClass('btn-warning').removeClass('btn-success');
        $('#pause').text('Pause')

        // Send Stop event and set local variables
        tweets = 0;
        running = false;
        var message = {message: "stop"}
        socket.send(JSON.stringify(message));
    });
}

function pause_or_resume(event) {
    // If running, pause
    if (running) {
        var message = {message: "pause"}
        socket.send(JSON.stringify(message));
        $(event.target).addClass('btn-success').removeClass('btn-warning');
        $(event.target).text('Resume')
        running = false;
    }
    // If not running, resume
    else {
        var message = {message: "resume"}
        socket.send(JSON.stringify(message));
        $(event.target).addClass('btn-warning').removeClass('btn-success');
        $(event.target).text('Pause')
        running = true;
    }
}

function newTweet(tweet) {
    tweet = JSON.parse(tweet);
    ++tweets;
    var date = moment(tweet.created_at, "ddd MMM DD HH:mm:ss ZZ YYYY").format("h:mmA");
    var linked_text = Autolinker.link(tweet.text);
    $('#screen2_tweets').prepend('<div class="row tweet"><div class="col-sm-1"><a href="#" class="pull-right"><img src="' + tweet.user.profile_image_url + '" class="tweet-profile_img"></a></div><div class="col-sm-11"><h3>' + tweet.user.name + ' <small>@' + tweet.user.screen_name + ' · ' + date + '</small></h3><h3>' + linked_text + '</h3></div></div><hr>');

    if (tweets > TWEET_LIMIT) {
        $('.tweet').last().remove()
        $('hr').last().remove()
    }
}