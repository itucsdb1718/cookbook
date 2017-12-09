

var empty = true;

function clearChat() {
    $(".chat-frame").empty();
}


function addMessage(parameters) {
    var who = parameters.who;
    var text = parameters.text;
    var time = parameters.time;
    var picture = parameters.picture;
    var viewed = parameters.viewed;
    var side = "right";
    var reverse = "left"
    var color = "darker";

    if (empty){
        clearChat();
        empty = false;
    }

    if (who !== "me") {
        side = "left";
        reverse = "right"
        color = "";
    }

    control = '<div class="row">' +
                  '<div class="chat-container ' + color + '">' +
                      '<img src="' + picture + '" alt="Avatar" class="' + side + '">' +
                      '<p>' + text + '</p>' +
                      '<span class="time-' + reverse + '">' + time + '</span>' +
                  '</div>\n' +
              '</div>'

    $(".chat-frame").append(control);
    $(".chat-frame").scrollTop($(".chat-frame")[0].scrollHeight);
}


/*
addMessage({who: "me", text: "Hello Tom...", time: 0, picture: "/uploads/default_profile.png"});
addMessage({who: "you", text: "Hi, Pablo", time: 1500, picture: "/uploads/default_profile.png"});
addMessage({who: "me", text: "What would you like to talk about today?", time: 3500, picture: "/uploads/default_profile.png"});
addMessage({who: "you", text: "Tell me a joke", time: 7000, picture: "/uploads/default_profile.png"});
addMessage({who: "me", text: "Spaceman: Computer! Computer! Do we bring battery?!", time: 9500, picture: "/uploads/default_profile.png"});
addMessage({who: "you", text: "LOL", time: 12000});
*/


function strftime(sFormat, date) {
  if (!(date instanceof Date)) date = new Date();
  var nDay = date.getDay(),
    nDate = date.getDate(),
    nMonth = date.getMonth(),
    nYear = date.getFullYear(),
    nHour = date.getHours(),
    aDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    aMonths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    aDayCount = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
    isLeapYear = function() {
      if ((nYear&3)!==0) return false;
      return nYear%100!==0 || nYear%400===0;
    },
    getThursday = function() {
      var target = new Date(date);
      target.setDate(nDate - ((nDay+6)%7) + 3);
      return target;
    },
    zeroPad = function(nNum, nPad) {
      return ('' + (Math.pow(10, nPad) + nNum)).slice(1);
    };
  return sFormat.replace(/%[a-z]/gi, function(sMatch) {
    return {
      '%a': aDays[nDay].slice(0,3),
      '%A': aDays[nDay],
      '%b': aMonths[nMonth].slice(0,3),
      '%B': aMonths[nMonth],
      '%c': date.toUTCString(),
      '%C': Math.floor(nYear/100),
      '%d': zeroPad(nDate, 2),
      '%e': nDate,
      '%F': date.toISOString().slice(0,10),
      '%G': getThursday().getFullYear(),
      '%g': ('' + getThursday().getFullYear()).slice(2),
      '%H': zeroPad(nHour, 2),
      '%I': zeroPad((nHour+11)%12 + 1, 2),
      '%j': zeroPad(aDayCount[nMonth] + nDate + ((nMonth>1 && isLeapYear()) ? 1 : 0), 3),
      '%k': '' + nHour,
      '%l': (nHour+11)%12 + 1,
      '%m': zeroPad(nMonth + 1, 2),
      '%M': zeroPad(date.getMinutes(), 2),
      '%p': (nHour<12) ? 'AM' : 'PM',
      '%P': (nHour<12) ? 'am' : 'pm',
      '%s': Math.round(date.getTime()/1000),
      '%S': zeroPad(date.getSeconds(), 2),
      '%u': nDay || 7,
      '%V': (function() {
              var target = getThursday(),
                n1stThu = target.valueOf();
              target.setMonth(0, 1);
              var nJan1 = target.getDay();
              if (nJan1!==4) target.setMonth(0, 1 + ((4-nJan1)+7)%7);
              return zeroPad(1 + Math.ceil((n1stThu-target)/604800000), 2);
            })(),
      '%w': '' + nDay,
      '%x': date.toLocaleDateString(),
      '%X': date.toLocaleTimeString(),
      '%y': ('' + nYear).slice(2),
      '%Y': nYear,
      '%z': date.toTimeString().replace(/.+GMT([+-]\d+).+/, '$1'),
      '%Z': date.toTimeString().replace(/.+\((.+?)\)$/, '$1')
    }[sMatch] || sMatch;
  });
}

