var canvas, ctx, flag = false,
    prevX = 0,
    currX = 0,
    prevY = 0,
    currY = 0,
    dot_flag = false;

var x = "black",
    y = 1;

function init() {
    canvas = document.getElementById('can');
    ctx = canvas.getContext("2d");
    w = canvas.width;
    h = canvas.height;

    canvas.addEventListener('touchmove', function(e) {
        findxytouch('move', e)
    }, false);
    canvas.addEventListener('touchstart', function(e) {
        findxytouch('down', e)
    }, false);
    canvas.addEventListener('touchend', function(e) {
        findxytouch('up', e)
    }, false);
    canvas.addEventListener('touchcancel', function(e) {
        findxytouch('out', e)
    }, false);
    canvas.addEventListener('mousemove', function(e) {
        findxymouse('move', e)
    }, false);
    canvas.addEventListener('mousedown', function(e) {
        findxymouse('down', e)
    }, false);
    canvas.addEventListener('mouseup', function(e) {
        findxymouse('up', e)
    }, false);
    canvas.addEventListener('mouseout', function(e) {
        findxymouse('out', e)
    }, false);
}


function draw() {
    ctx.beginPath();
    ctx.moveTo(prevX, prevY);
    ctx.lineTo(currX, currY);
    ctx.strokeStyle = x;
    ctx.lineWidth = y;
    ctx.stroke();
    ctx.closePath();
}

function erase() {
    ctx.clearRect(0, 0, w, h);


}

function save() {
    document.getElementById("prediction").innerHTML = "prediction: LOADING..."
    var dataURL = canvas.toDataURL();

    canvas.toBlob(
        blob => {
            var formdata = new FormData();

            formdata.append("test_image", blob, "run.jpg");
            $.ajax({
                url: "/keview/v1alpha/run/",
                type: "POST",
                data: formdata,
                processData: false,
                contentType: false,
                success: function(data) {

                    document.getElementById("prediction").innerHTML = "prediction: " + data["prediction"]
                }
            }).done(function(respond) {});
        })


}

function findxytouch(res, e) {
    if (res == 'down') {
        prevX = currX;
        prevY = currY;
        currX = e.touches[0].clientX - canvas.offsetLeft;
        currY = e.touches[0].clientY - canvas.offsetTop;
        flag = true;
        dot_flag = true;
        if (dot_flag) {
            ctx.beginPath();
            ctx.fillStyle = x;
            ctx.fillRect(currX, currY, 2, 2);
            ctx.closePath();
            dot_flag = false;
        }
    }
    if (res == 'up' || res == "out") {
        flag = false;
    }
    if (res == 'move') {
        if (flag) {
            prevX = currX;
            prevY = currY;
            currX = e.touches[0].clientX - canvas.offsetLeft;
            currY = e.touches[0].clientY - canvas.offsetTop;
            draw();
        }
    }
}

function findxymouse(res, e) {
    if (res == 'down') {
        prevX = currX;
        prevY = currY;
        currX = e.clientX - canvas.offsetLeft;
        currY = e.clientY - canvas.offsetTop;
        flag = true;
        dot_flag = true;
        if (dot_flag) {
            ctx.beginPath();
            ctx.fillStyle = x;
            ctx.fillRect(currX, currY, 2, 2);
            ctx.closePath();
            dot_flag = false;
        }
    }
    if (res == 'up' || res == "out") {
        flag = false;
    }
    if (res == 'move') {
        if (flag) {
            prevX = currX;
            prevY = currY;
            currX = e.clientX - canvas.offsetLeft;
            currY = e.clientY - canvas.offsetTop;
            draw();
        }
    }
}