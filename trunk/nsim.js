// vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

var lastCmd = null;

function getRemoteUrl()
{
    formVal = $('#rpc-url').val();
    if (formVal.length > 0)
        return formVal; 

    return document.URL;
}

function updateInfo()
{
    var now = new Date();
    var nowStr = now.toLocaleTimeString();
    $('#info-last-update').html(nowStr);

    $.ajax({
        url: getRemoteUrl(),
        crossDomain: true,
        data: JSON.stringify({ cmd: "status" }),
        dataType: 'json',
        type: 'POST',
        success: processStatus 
    });

    $.ajax({
        url: getRemoteUrl(),
        crossDomain: true,
        data: JSON.stringify({ cmd: "modules" }),
        dataType: 'json',
        type: 'POST',
        success: processModules
    });
}

function processStatus(json)
{
    $('#info-version').html(json.version);
}

function processModules(json) {
    modules = ""
    for (var i = 0; i < json.modules.length; i++)
        modules += json.modules[i].name + '&nbsp;';
    $('#info-modules').html(modules);
}

function sendCmd()
{
    var cmdStr = $("#console").val();
    cmdStr = cmdStr.split('\n').join("")
    lastCmd = cmdStr;
    $("textarea#console").val("");

    var cmdParams = cmdStr.split(" ");
    var cmdPart = cmdParams[0]
    cmdParams.shift();
    var cmdParts = cmdPart.split(":");
    request = {};
    if (cmdParts.length == 1)
    {
        request['cmd'] = cmdParts[0];
    }
    else
    {
        request['module'] = cmdParts[0];
        request['cmd'] = cmdParts[1];
    }

    for (var i = 0; i < cmdParams.length; i++)
    {
        t = cmdParams[i].split("="); 
        if (t.length == 2)
            if (typeof(t[0]) == 'string')
            {
                key = t[0];
                val = t[1];
                valRaw = val.match(/^["']([^"']*)["']$/);
                // check if value should be interpreted as string or number
                if (val.length > 1 && valRaw != null)
                {
                    val = valRaw[1];
                }
                else
                {
                    // try to convert string to int, if not successfull, leave value as string
                    val = parseInt(t[1]);
                    if (val == NaN)
                        val = t[1]
                }
                request[key] = val;
            }
    }
    
    $.ajax({
        url: getRemoteUrl(),
        crossDomain: true,
        data: JSON.stringify(request),
        dataType: 'json',
        type: 'POST',
        success: processCmd,
        error: processCmdError
    });
}

function processCmd(json)
{
    output = "<div class=\"console-output-item\">";
    output += "  <div class=\"console-output-cmd\">&gt;&nbsp;" + lastCmd + "</div>";
    output += "  <div class=\"console-output-result\">";
    if ($('#console-indent-output').prop('checked'))
        output += JSON.stringify(json, undefined, 2);
    else
        output += JSON.stringify(json);
    output += "  </div>";
    output += "</div>";

    $('#console-output').prepend(output);
}

function processCmdError(jqXHR, textStatus, errorThrown)
{
    output = "<div class=\"console-output-item\">";
    output += "  <div class=\"console-output-cmd\">&gt;&nbsp;" + lastCmd + "</div>";
    output += '<div style="color: red;">Http error occured: ' + textStatus + ' ' + errorThrown + '</div>';

    output += "</div>";
    $('#console-output').prepend(output);
}


$(document).ready(function() {

    $('#rpc-url').val(document.URL + "soap");

    updateInfo();

    $('#console').keydown(function(e)
    {
        if (e.keyCode == 13)
        {
            sendCmd();
        }
    });

});


