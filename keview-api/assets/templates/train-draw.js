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
    var dataURL = canvas.toDataURL();
    var type = document.getElementById("fname").value
    console.log(type)
    if (!canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data
        .some(channel => channel !== 0)) {
        alert("draw a number!")
    } else {
        if (type != "") {
            canvas.toBlob(
                blob => {
                    var formdata = new FormData();

                    formdata.append("test_image", blob, type + ".jpg");
                    $.ajax({
                        url: "/keview/v1alpha/store-train-image/",
                        type: "POST",
                        data: formdata,
                        processData: false,
                        contentType: false,
                    }).done(function(respond) {});
                    erase()
                    document.getElementById("fname").value = ""
                })
        } else {
            alert("number is missing!")
        }
    }

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