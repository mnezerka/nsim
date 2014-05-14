// vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

var realtime = false;
var realtimeId = null;
var lastCmd = null;

function getRemoteUrl()
{
    formVal = $('#rpc-url').val();
    if (formVal.length > 0)
        return formVal; 

    return remoteUrl;
}

function refreshStatus()
{
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
    console.log("processModules called");
    modules = ""
    for (var i = 0; i < json.modules.length; i++)
    {
        modules += json.modules[i].name + '&nbsp;';
    }
    $('#info-modules').html(modules);

}

function updateInfo()
{
    console.log('Updating state');
    var now = new Date();
    refreshStatus();
    var nowStr = now.toLocaleTimeString();
    $('#info-last-update').html(nowStr);
    $('#rpc-url').val(getRemoteUrl());
}

function setRealtime()
{
    if (!realtime)
    {
        console.log("enabling realtime");
        realtimeId = setInterval(updateState, 5000);
        $('#realtime').text("Disable Realtime");
        realtime = true;
    }
    else
    {
        console.log("disabling realtime");
        clearInterval(realtimeId);
        $('#realtime').text("Enable Realtime");
        realtime = false;
    }
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
    if (cmdParts.length == 1)
    {
        cmdModule = "nsim";
        cmd = cmdParts[0];
    }
    else
    {
        cmdModule = cmdParts[0];
        cmd = cmdParts[1];
    }
         
    $.ajax({
        url: getRemoteUrl(),
        crossDomain: true,
        data: JSON.stringify({ module: cmdModule, cmd: cmd, params: cmdParams}),
        dataType: 'json',
        type: 'POST',
        success: processCmd
    });
}

function processCmd(json)
{
    console.log("processing command");

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

$(document).ready(function() {
    updateInfo();
    getRemoteUrl();

    $('#console').keydown(function(e)
    {
        if (e.keyCode == 13)
        {
            sendCmd();
        }
    });

});


