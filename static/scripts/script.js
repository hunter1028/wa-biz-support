let conversationContext = '';
let recorder;
let context;

function displayMsgDiv(content, type, who) {
  const time = new Date();
  let hours = time.getHours();
  let minutes = time.getMinutes();
  const ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour "0" should be "12"
  hours = hours < 10 ? '0' + hours : hours;
  minutes = minutes < 10 ? '0' + minutes : minutes;
  const strTime = hours + ':' + minutes + ' ' + ampm;

  let msgHtml = "";
  let display_v = "";

  if (who == 'bot') {
	   msgHtml = "<div class='jss17'><img src='./static/img/help.png' class='jss20'>	<div class='jss23'>	";
  }else{
	  msgHtml = "<div class='jss18'><div class='jss21'>";
  }
  
  if(typeof content == 'string'){
	  if (who == 'bot') {
		  msgHtml += "<div class='jss24'>"; 
	  }
	  display_v = content.replace(/(\r\n)|(\n)/g,'<br>');
	  msgHtml += display_v;
	  if (who == 'bot') {
		  msgHtml += "</div>";
	  }
  }else if (typeof content == 'object') {
	  if(type == 'text'){
		  msgHtml += "<div class='jss24'>";
		  display_v =content[0].replace(/(\r\n)|(\n)/g,'<br>');
		  msgHtml += display_v;
		  msgHtml += "</div>";
	  }else{
		  msgHtml += "<div class='jss25'>";
		  msgHtml += content.title;
		  msgHtml += "</div>";
		  
		 
		  for(var i=0;i<content.options.length;i++){
			  msgHtml += "<div class='jss26' onclick='sendMessage($(this).html())'>";
			  display_v +=  content.options[i].value.input.text;
			  msgHtml += display_v+ "</div>";
			  display_v = "";
		      
		  } 
	  }
  }

// msgHtml += "</div><div class='" + who + "-line'>" + strTime + '</div></div>';
  if (who == 'bot') {
	  msgHtml += "</div></div>";
  }else{
	  msgHtml += "</div></div>";
  }
  
  $('#messages').append(msgHtml);
  $('#messages').scrollTop($('#messages')[0].scrollHeight);

  if (who == 'user') {
    $('#q').val('');
// $('#q').attr('disabled', 'disabled');
    $('#p2').fadeTo(500, 1);
  } else {
    $('#q').removeAttr('disabled');
    $('#p2').fadeTo(500, 0);
  }
}

$(document).ready(function() {
// $('#q').attr('disabled', 'disabled');
  $('#p2').fadeTo(500, 1);
  $('#h').val('0');

  $.ajax({
    url: '/api/conversation',
    convText: '',
    context: ''
  })
    .done(function(res) {
      conversationContext = res.results.context;
      displayMsgDiv(res.results.reponseContent,　res.results.responseType,  'bot');
// play(res.results.responseText);
    })
    .fail(function(jqXHR, e) {
      console.log('Error: ' + jqXHR.responseText);
    })
    .catch(function(error) {
      console.log(error);
    });
});

function clickEnter(){
	var code = event.keyCode;
	
	if(code == 13){
		var message = $('#q').val().trim();
		sendMessage(message)
		 $('#q').val('');
}
}	
function sendMessage(message){
	if(message==''){
		return;
	}
	displayMsgDiv(message, 'user');
	
     var form = new FormData();
     form.append("convText","message");
     var req = new XMLHttpRequest();
     
		    $.post('/api/conversation', {
		    		convText: message,
		    		context: JSON.stringify(conversationContext)
		    	})
		    .done(function(res) {
		      conversationContext = res.results.context;
//play(res.results.responseText);
		      displayMsgDiv(res.results.reponseContent,res.results.responseType, 'bot');
		    })
		    .fail(function(jqXHR, e) {
		      console.log('Error: ' + jqXHR.responseText);
		    });
}

function callConversation(res) {
  // $('#q').attr('disabled', 'disabled');

  $.post('/api/conversation', {
    convText: res,
    context: JSON.stringify(conversationContext)
  })
    .done(function(res, status) {
      conversationContext = res.results.context;
//      play(res.results.responseText);
      displayMsgDiv(res.results.reponseContent, res.results.responseType,'bot');
    })
    .fail(function(jqXHR, e) {
      console.log('Error: ' + jqXHR.responseText);
    });
}

function play(inputText) {
  let buf;
  
  const url = '/api/text-to-speech';
  const params = 'text=' + inputText;
  const request = new XMLHttpRequest();
  request.open('POST', url, true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  request.responseType = 'arraybuffer';

  // Decode asynchronously
  request.onload = function() {
    context.decodeAudioData(
      request.response,
      function(buffer) {
        buf = buffer;
        play();
      },
      function(error) {
        console.error('decodeAudioData error', error);
      }
    );
  };
  request.send(params);

  // Play the loaded file
  function play() {
    // Create a source node from the buffer
    const source = context.createBufferSource();
    source.buffer = buf;
    // Connect to the final output node (the speakers)
    source.connect(context.destination);
    // Play immediately
    source.start(0);
  }
}

const recordMic = document.getElementById('stt2');
recordMic.onclick = function() {
  const fullPath = recordMic.src;
  const filename = fullPath.replace(/^.*[\\/]/, '');
  if (filename == 'mic.gif') {
    try {
      recordMic.src = './static/img/mic_active.png';
      startRecording();
      console.log('recorder started');
      $('#q').val('');
      $('#q').attr('placeholder','お話しください。聞いております...');
    } catch (ex) {
      // console.log("Recognizer error .....");
    }
  } else {
    stopRecording();
    $('#q').attr('placeholder','メッセージを送信...');
    recordMic.src = './static/img/mic.gif';
  }
};

function startUserMedia(stream) {
  
 
}

function startRecording(button) {
  recorder && recorder.record();
  console.log('Recording...');
}

function stopRecording(button) {
  recorder && recorder.stop();
  console.log('Stopped recording.');

  recorder &&
    recorder.exportWAV(function(blob) {
      console.log(blob);
      const url = '/api/speech-to-text';
      const request = new XMLHttpRequest();
      request.open('POST', url, true);
      // request.setRequestHeader('Content-Type',
		// 'application/x-www-form-urlencoded');

      // Decode asynchronously
      request.onload = function() {
    	  if(request.response.trim() != ''){
    		  displayMsgDiv(request.response, 'user');
    		  callConversation(request.response);
    	  }else{
    		  displayMsgDiv('聞き取れませんでした。もう一度お試しください。', 'text', 'bot');
    		  
    	  }
      };
      request.send(blob);
    });

  recorder.clear();
}

window.onload = function init() {
  try {
    // webkit shim
   
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia ||navigator.msGetUserMedia;
    
    var constraints = {audio: true};
    

    	 
    console.log('Audio context set up.');
    //console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    alert('No web audio support in this browser!');
  }
  
  navigator.mediaDevices.getUserMedia(constraints)
  .then(function (stream){
	  window.AudioContext = window.AudioContext || window.webkitAudioContext;
	  window.URL = window.URL || window.webkitURL;
	  context = new AudioContext();
	  const input = context.createMediaStreamSource(stream);
	  console.log('Media stream created.');
	  // Uncomment if you want the audio to feedback directly
	  // input.connect(audio_context.destination);
	  // console.log('Input connected to audio context destination.');

	  // eslint-disable-next-line
	  recorder = new Recorder(input);
	  console.log('Recorder initialised.');
	  
  })
  .catch(function(e) {
	  console.log('No live audio input: ' + e);
  });

};
