$(function () {
    var INDEX = 0;
    var recognition;
    var uniqueSessionId;
    var COSINE_THRESHOLD = 0.7 // Change as per requirement
    var pythonApiURL = "http://localhost:5000";

    var initializeSession = function () {
        $(".chat-logs").empty();
        uniqueSessionId = getUniqueChatSessionId();
        generateMessage("Hi, please send the message you would like to verify", 'bot');
        enableInput();
        $("#loading").hide();
    };

    function sendChatMessage(message) {
        $("#loading").show();

        talkToPythonAPI(message);
        generateMessage(message, 'user');
    }

    function generateMessage(msg, type) {
        INDEX++;
        var str = "";
        str += "<div id='cm-msg-" + INDEX + "' class=\"chat-msg " + type + "\">";
        str += "          <span class=\"msg-avatar\">";
        if (type === 'bot') {
            str += "            <img src=\"b_logo.png\">";
        } else {
            str += "            <img src=\"user-logo.png\">";
        }

        str += "          <\/span>";
        str += "          <div class=\"cm-msg-text\">";
        str += msg;
        str += "          <\/div>";
        str += "        <\/div>";
        $(".chat-logs").append(str);
        $("#cm-msg-" + INDEX).hide().fadeIn(300);
        if (type === 'user') {
            $("#chat-input").val('');
        }
        $(".chat-logs").stop().animate({
            scrollTop: $(".chat-logs")[0].scrollHeight
        }, 1000);
    }

    function talkToPythonAPI(text) {
        $.ajax({
            type: "POST",
            url: pythonApiURL + "/verifyMessage",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            // headers: {
            //     "Authorization": "Bearer " + dialogflowAccessToken
            // },
            data: JSON.stringify({
                message: text,
                cosineThreshold: COSINE_THRESHOLD,
            }),
            success: pythonSuccessResponse,
            error: pythonErrorResponse
        });
    }

    var pythonSuccessResponse = function (data) {
        $("#loading").hide();
        enableInput();
        // console.log(data.result)
        generateMessage(data.result, 'bot');
    };

    var pythonErrorResponse = function (data) {
        $("#loading").hide();
        generateMessage("Error occured. Please try again later", 'bot');
    };

    var enableInput = function () {
        $("#chat-input").focus();
        $("#chatBotForm").children().prop("disabled", false);
        $('#micSpan').show();
    };

    var disableInput = function () {
        $("#chatBotForm").children().prop("disabled", true);
        $('#micSpan').hide();
    };

    $(document).delegate(".chat-btn", "click", function () {
        var msg = $(this).attr("chat-value");
        enableInput();

        talkToPythonAPI(msg);
        generateMessage(msg, 'user');
    });

    $('#tip-close').click(function () {
        $('.tool_tip').remove();
    });

    $("#chat-circle, #tip-tool").click(function () {
        $('.tool_tip').remove();
        $("#chat-circle").toggle('scale');
        $(".chat-box").toggle('scale');
        $(".chat-logs").stop().animate({
            scrollTop: $(".chat-logs")[0].scrollHeight
        }, 1000);
    });

    $(".chat-box-toggle").click(function () {
        $("#chat-circle").toggle('scale');
        $(".chat-box").toggle('scale');
    });

    $("#chat-submit").click(function (e) {
        e.preventDefault();
        var msg = $("#chat-input").val();
        if (msg.trim() === '') {
            return false;
        }

        sendChatMessage(msg);
    });

    $("#refresh").click(function () {
        initializeSession();
    });

    $("#mic").click(function (event) {
        switchRecognition();
    });

    function stopRecognition() {
        if (recognition) {
            recognition.stop();
            recognition = null;
        }

        updateRec();
    }

    function startRecognition() {
        recognition = new webkitSpeechRecognition();
        recognition.onstart = function (event) {
            updateRec();
        };
        recognition.onresult = function (event) {
            var text = "";
            for (var i = event.resultIndex; i < event.results.length; ++i) {
                text += event.results[i][0].transcript;
            }
            console.log(text);
            sendChatMessage(text);
            stopRecognition();
        };
        recognition.onend = function () {
            stopRecognition();
        };
        recognition.lang = "en-US";
        recognition.start();
    }

    function switchRecognition() {
        if (recognition) {
            stopRecognition();
        } else {
            startRecognition();
        }
    }

    function updateRec() {
        $("#mic").text(recognition ? "stop" : "mic");
    }

    function getUniqueChatSessionId() {
        var s4 = function () {
            return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
        };
        return s4() + s4() + "-" + s4() + "-" + s4() + "-" +
            s4() + "-" + s4() + s4() + s4();
    }

    initializeSession();
});