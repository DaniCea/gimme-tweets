var socket = io.connect('http://' + document.domain + ':' + location.port + '/tweets', {'force new connection': true });

var TWEET_LIMIT = 100;

nunjucks.configure('views', { autoescape: true });

var running = false;
var tweets = 0;

$(function() {
    $("#start").on("click", function( e ) {
        start(e);
    });

    $("#stop").on("click", function( e ) {
        stop(e);
    });

    $("#pause").on("click", function( e ) {
        pause_or_resume(e)
    });

    $('#query').on('keyup', function(e) {
        var length = $(this).val().length;
        if (length > 0) {
            $("#start").addClass('enabled').removeClass('disabled');
        }
        else {
            $("#start").addClass('disabled').removeClass('enabled');    
        }
    });
});

socket.on('tweet', function(tweet) {
    newTweet(tweet);
});

function start(event) {
    if ($(event.target).hasClass('disabled')) return;
    // Unhide tweet section
    $('#tweets').show();

    // Scroll to it
    $("body").animate({ 
        scrollTop: $('#tweets').offset().top 
    }, 600, "swing", function() {
        // Send Start event and set local variables
        running = true;
        socket.emit("start", $("#query").val());

        // Hide & cleanup header section
        $(".header").hide();
        $("#query").val("");
        $("#start").addClass("disabled").removeClass("enabled");
    });   
}

function stop(event) {
    $(".header").show();
    $("body").animate({
        scrollTop: $('#tweets').offset().top
    }, 0);
    $("body").animate({ 
        scrollTop: $(".header").offset().top 
    }, 600, "swing", function() {
        $('#tweets').hide();
        $('#main').empty();

        // Send Stop event and set local variables
        tweets = 0;
        running = false;
        socket.emit('stop');
    });
}

function pause_or_resume(event) {
    // If running, pause
    if (running) {
        socket.emit('pause');
        $(event.target).addClass('btn-success').removeClass('btn-warning');
        $(event.target).text('Resume')
        running = false;
    }
    // If not running, resume
    else {
        socket.emit('resume');
        $(event.target).addClass('btn-warning').removeClass('btn-success');
        $(event.target).text('Pause')
        running = true;
    }    
}

function newTweet(tweet) {
    ++tweets;
    var date = moment(tweet.created_at, "ddd MMM DD HH:mm:ss ZZ YYYY").format("h:mmA");
    tweet.date = date;
    $('#main').prepend(nunjucks.render('/static/templates/tweet.html', tweet));

    if (tweets > TWEET_LIMIT) {
        $('.tweet').last().remove()
        $('hr').last().remove()
    }
}