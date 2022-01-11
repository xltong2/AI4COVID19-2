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

var divRecording;
var divShowResult;
var btnBack;

// get microphone device
navigator.mediaDevices.getUserMedia({audio:true}).then (stream => {handlerFunction(stream)})

// redirect
function redirect_dashboard() {
    location.href = '../dashboard';
}

function handlerFunction(stream) {
    rec = new MediaRecorder(stream); 
    audioChunks = []; 

    //once the recording is started
    rec.ondataavailable = e => {
        audioChunks.push(e.data);
    }

    //once the recording is stopped
    rec.onstop = e => { 
        audioBlob = new Blob(audioChunks, {type:'audio/mp3'}); //new blob defined as mp3
        console.log(audioBlob);

        // ---- test to download ----
        // var element = document.createElement('a');
        // element.style.display = 'none';
        // element.href = URL.createObjectURL(audioBlob);
        // document.body.appendChild(element);
        // element.download = 'myfile';
        // element.click();
        // URL.revokeObjectURL(element.href);
        // element.parentNode.removeChild(element);

        if(recordingCount == 6){

            var formData = new FormData();
            formData.append('audio', audioBlob, 'audio.mp3');
            $.ajax({
                type: "POST",
                url: "/diagnose/",
                data: formData,
                processData: false,  // prevent jQuery from converting the data
                contentType: false,  // prevent jQuery from overriding content type
            })
        }
        // --- for reference ---
        //var audioUrl = URL.createObjectURL(audioBlob);
        // recordedAudio.src = URL.createObjectURL(audioBlob); //show the audio file
        // recordedAudio.controls=true; //allow user to control (e.g. play or download audio)
    }
}

function OnButtonDown (btnMicrophoneBorder) {
    btnMicrophoneBorder.style.visibility = "visible";
    recordingCount += 1;
    Visibility ();
    rec.start();
}

function OnButtonUp (btnMicrophoneBorder) {
    btnMicrophoneBorder.style.visibility = "hidden";
    recordingCount += 1;
    Visibility ();
    rec.stop();
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
            break;
        case 4:
            msgSecondCoughing.style.display = "none";
            msgSecondCoughDone.style.display = "flex";
            break;
        case 5:
            msgSecondCoughDone.style.display = "none";
            msgThirdCoughing.style.display = "flex";
            break;
        case 6:
            msgThirdCoughing.style.display = "none";
            msgThirdCoughDone.style.display = "flex";
            divRecording.style.display = "none";
            divShowResult.style.display = "flex";
            btnBack.style.display = "none";
            break;
    }
}

function Init () {
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

    divRecording = document.getElementById ("div_recording");
    divShowResult = document.getElementById ("div_view_result");
    btnBack = document.getElementById ('btn_back');
    
    //test
    // rec.start();
    // rec.stop();
    //test

    if (btnMicrophone.addEventListener) {  // all browsers except IE before version 9
        btnMicrophone.addEventListener ("mousedown", function () {OnButtonDown (btnMicrophoneBorder)}, false);
        btnMicrophone.addEventListener ("mouseup", function () {OnButtonUp (btnMicrophoneBorder)}, false);
    }
}