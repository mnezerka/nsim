// vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

var realtime = false;
var realtimeId = null;

function refreshStatus()
{
    $.ajax({
        url: "http://localhost:9999/soap",
        crossDomain: true,
        data: JSON.stringify({ cmd: "status" }),
        dataType: 'json',
        type: 'POST',
        success: processStatus 
    });
}

function processStatus(json)
{
    //$('status-version').text(json.version);
    $('#status-status').html(json.status);
    $('#status-version').html(json.version);
}

function queryModules() 
{
    $.ajax({
        url: "http://localhost:9999/soap",
        crossDomain: true,
        data: JSON.stringify({ cmd: "modules" }),
        dataType: 'json',
        type: 'POST',
        success: processModules
    });
}

function processModules(json) {
    console.log("processModules called");
    $('#modules').find('tr:gt(0)').remove();
    for (var i = 0; i < json.modules.length; i++)
    {
        var row = document.createElement('tr');
        var tdName = document.createElement('td');
        var tdInfoChannels = document.createElement('td');
        var tdCommands = document.createElement('td');
        tdName.innerHTML = json.modules[i].name;
        row.appendChild(tdName)

        // info channels
        var infoChannels = '';
        for (var ic = 0; ic < json.modules[i].infochannels.length; ic++)
        {
            var spanChannel = document.createElement('span');
            var cbChannel = document.createElement('input');
            cbChannel.type = 'checkbox';
            cbChannel.name = json.modules[i].name + '::' + json.modules[i].infochannels[ic].name;
            cbChannel.value = '1';
            spanChannel.appendChild(cbChannel);
            spanChannel.appendChild(document.createTextNode(json.modules[i].infochannels[ic].name));
            tdInfoChannels.appendChild(spanChannel);
        }
        row.appendChild(tdInfoChannels)

        // commands
        var commands = '';
        for (var ic = 0; ic < json.modules[i].commands.length; ic++)
        {
            var spanCommand = document.createElement('span');
            spanCommand.appendChild(document.createTextNode(json.modules[i].commands[ic].name));
            tdCommands.appendChild(spanCommand);
        }
        row.appendChild(tdCommands)

        $('#modules').find('tbody').append(row);
    }
}

function updateState()
{
    console.log('Updating state');
    var now = new Date();
    refreshStatus();
    var nowStr = now.toLocaleTimeString();
    $('#status-last-update').html(nowStr);

    // loop through all info channels
    $('input[type=checkbox]').each(function()
    {
        if (this.checked)
        {
            name = $(this).attr('name');
            parts = name.split('::'); 
            if (parts.length != 2)
                return; 
            module = parts[0];
            infoChannel = parts[1];

            // send json request to fetch info channel
            console.log('module: ' + module + ', info channel: ' + infoChannel);

            queryInfoChannel(module, infoChannel);
        }
    });
}

function queryInfoChannel(module, channel)
{
    $.ajax({
        url: "http://localhost:9999/soap",
        crossDomain: true,
        data: JSON.stringify({ module: module, channel: channel}),
        dataType: 'json',
        type: 'POST',
        success: processInfoChannel
    });
}

function processInfoChannel(json)
{
    id = 'channel-' + json.module + '-' + json.channel; 
    console.log('processing info channel' + id);

    channelsDiv = document.getElementById('info-channels');

    // create channel div if doesn't exist
    channelDiv = document.getElementById(id);
    if (!channelDiv)
    {
        channelDiv = document.createElement('div');
        channelDiv.id = id;
        channelDiv.className = 'info-channel';
        channelsDiv.appendChild(channelDiv);
    }

    // remove previous content
    while (channelDiv.firstChild) { channelDiv.removeChild(channelDiv.firstChild); }

    // create title
    channelTitleDiv = document.createElement('div');
    channelTitleDiv.className = 'channel-title';
    channelTitleDiv.appendChild(document.createTextNode('Info channel: ' + json.channel));
    channelDiv.appendChild(channelTitleDiv);

    // loop through channel data array and create html output
    channelData = json.data;
    if (channelData instanceof Array)
    {
        for (i = 0; i < channelData.length; i++)
        {
            line = document.createElement('div');
            line.className = 'line';
            line.appendChild(document.createTextNode(channelData[i]));
            channelDiv.appendChild(line);
        }
    }

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

function runCmd()
{
    var cmdStr = $("#cmd").val();
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
        url: "http://localhost:9999/soap",
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
}

$(document).ready(function() {
    //$('#status-refresh').on('click', refreshStatus);
    //$('#modules-refresh').on('click', refreshModules);
    queryModules();
    updateState();
    $('#realtime').on('click', setRealtime);
    $('#update').on('click', updateState);
    $('#runcmd').on('click', runCmd);

});


