var recordingCount;
var btnMicrophone;
var btnMicrophoneBorder;

var msgBeforeCoughing;
var msgFirstCoughing;
var msgFirstCoughDone;
var msgSecondCoughing;
var msgSecondCoughDone;
var msgThirdCoughing;
var msgThirdCoughDone;

var audioFirstCoughing;
var audioSecondCoughing;
var audioThirdChoughing;

var divRecording;
var divShowResult;
var btnBack;
var processingResult;
var viewResult;

var audio_context;
var recorder;

var url, div;


// redirect


window.onload = function Init() {
    recordingCount = 0;
    btnMicrophone = document.getElementById ("btn_microphone");
    btnMicrophoneBorder = document.getElementById ("btn_onclick_border");

    msgBeforeCoughing = document.getElementById ("msg_before_coughing");
    msgFirstCoughing = document.getElementById ("msg_first_coughing");
    msgFirstCoughDone = document.getElementById ("msg_first_cough_done");
    msgSecondCoughing = document.getElementById ("msg_second_coughing");
    msgSecondCoughDone = document.getElementById ("msg_second_cough_done");
    msgThirdCoughing = document.getElementById ("msg_third_coughing");
    msgThirdCoughDone = document.getElementById ("msg_third_cough_done");

    audioFirstCoughing = document.getElementById("audio_first_coughing");
    audioSecondCoughing = document.getElementById("audio_second_coughing");
    audioThirdChoughing = document.getElementById("audio_third_coughing");

    divRecording = document.getElementById ("div_recording");
    divShowResult = document.getElementById ("div_view_result");
    btnBack = document.getElementById ('btn_back');
    processingResult = document.getElementById("processing_result");
    viewResult = document.getElementById("view_result");

    try {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
      window.URL = window.URL || window.webkitURL;
      audio_context = new AudioContext;
    } catch (e) {
      alert('No web audio support here! diagnose.js');
    }
    navigator.getUserMedia({audio: true}, startUserMedia, function(e) {alert('No live audio input: ' + e);});

    if (btnMicrophone.addEventListener) {  // all browsers except IE before version 9
        btnMicrophone.addEventListener ("mousedown", function () {
            OnButtonDown (btnMicrophoneBorder);
            startRecording();
        }, false);
        btnMicrophone.addEventListener ("mouseup", function () {
            OnButtonUp (btnMicrophoneBorder);
            if (recordingCount < 6) {
                pauseRecording();
            } else {
                stopRecording();
            }
        }, false);
    }
}

function redirect_dashboard() {
    location.href = '../dashboard';
}

function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    // Uncomment for the audio to feedback directly
    // input.connect(audio_context.destination);
    recorder = new Recorder(input);
}

function startRecording() {
    audio_context.resume();
    recorder && recorder.record();
}

function pauseRecording() {
    recorder && recorder.stop();
    showAudio();
}

function stopRecording() {
    recorder && recorder.stop();

    recorder && recorder.exportWAV(function(blob) {
        // ---- test to download ----
        // var element = document.createElement('a');
        // element.style.display = 'none';
        // element.href = URL.createObjectURL(blob);
        // document.body.appendChild(element);
        // element.download = 'myfile';
        // element.click();
        // URL.revokeObjectURL(element.href);
        // element.parentNode.removeChild(element);
        
        // ajax
        var formData = new FormData();
        formData.append('audio', blob, 'audio.wav');
        $.ajax({
            type: "POST",
            url: "/diagnose/",
            data: formData,
            processData: false,  // prevent jQuery from converting the data
            contentType: false,  // prevent jQuery from overriding content type
        });
    });

    showAudio();

    recorder.clear();
}

function showAudio () {
    // create WAV download link using audio data blob
    recorder && recorder.exportWAV(function(blob) {
      url = URL.createObjectURL(blob);
      div = document.createElement('div');
      au = document.createElement('audio');
      au.controls = true;
      au.src = url;
      div.appendChild(au);
      if (recordingCount == 2) {
        audio_first_coughing.appendChild(div);
      }
      if (recordingCount == 4) {
        audio_second_coughing.appendChild(div);
      }
      if (recordingCount == 6) {
        audio_third_coughing.appendChild(div);
      }
    });
}

function hideAudio () {
    div.parentNode.removeChild(div);
    au.parentNode.removeChild(au);
}

function OnButtonDown (btnMicrophoneBorder) {
    btnMicrophoneBorder.style.visibility = "visible";
    recordingCount += 1;
    Visibility ();
}

function OnButtonUp (btnMicrophoneBorder) {
    btnMicrophoneBorder.style.visibility = "hidden";
    recordingCount += 1;
    Visibility ();
}

function Visibility () {
    switch (recordingCount) {
        case 1:
            msgBeforeCoughing.style.display = "none";
            msgFirstCoughing.style.display = "flex";
            break;
        case 2:
            msgFirstCoughing.style.display = "none";
            msgFirstCoughDone.style.display = "flex";
            break;
        case 3:
            msgFirstCoughDone.style.display = "none";
            msgSecondCoughing.style.display = "flex";
            hideAudio ();
            break;
        case 4:
            msgSecondCoughing.style.display = "none";
            msgSecondCoughDone.style.display = "flex";
            break;
        case 5:
            msgSecondCoughDone.style.display = "none";
            msgThirdCoughing.style.display = "flex";
            hideAudio ();
            break;
        case 6:
            msgThirdCoughing.style.display = "none";
            msgThirdCoughDone.style.display = "flex";
            divRecording.style.display = "none";
            divShowResult.style.display = "flex";
            btnBack.style.display = "none";
            setTimeout(function () {
                processingResult.style.display = "none";
                viewResult.style.display = "flex";
            }, 10000);
            break;
    }
}