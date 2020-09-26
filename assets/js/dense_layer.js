class InputElement {
    constructor(circle, line) {
        this.circle = circle;
        this.line = line;
    }
}
class SVGTextWithBg {
    constructor(text, background) {
        this.text = text;
        this.background = background;
    }
}
var selectedON = 0
var selectedIN = 0
unselectedNeuronHeight = "50px";
selectedNeuronHeight = "100px"
inputElements = []; //Input circle,lines
outputElements = []; //Circle
outputLine = null;
weightElement = null; //weight text, background
svg = document.getElementById("svg")
inputNeuronBox = document.getElementById("inputNeuronBox")
outputNeuronBox = document.getElementById("outputNeuronBox");
biasElement = document.getElementById("bias");
var outerBox = document.getElementById("outer-box")

function onload(neuronalWeights, neuronalInput) {

    components = JSON.parse(neuronalWeights)


    setInputNeurons(JSON.parse(neuronalInput))
    setOutpuNeurons()

}

function setInputNeurons(input) {

    weights = []
    components.forEach((item, i, self) => weights[i] = item.weights);
    firstCircle = null
    offsetInput = 0
    if (Math.min(input) < 0) {
        offsetInput = Math.min(...input) * -1
    }
    maxInputValue = Math.max(...input)
    for (var i = 0; i < input.length; i++) {

        var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('id', i + "CircleLine")
        line.setAttribute('x1', '0');
        line.setAttribute('y1', '0');
        line.setAttribute('x2', '200');
        line.setAttribute('y2', '200');
        line.setAttribute("stroke", "black")
        svg.appendChild(line)

        var circle = document.createElement("div");
        circle.className = "circle"
        circle.setAttribute("onmouseover", "selectInputNeuron(this)")
        bgColor = perc2color((offsetInput + input[i]) / (offsetInput + maxInputValue))
        circle.style.backgroundColor = bgColor
        circle.style.color = getContrastYIQ(bgColor)
        var span = document.createElement('span');
        span.textContent = input[i].toFixed(4);
        circle.appendChild(span);
        inputNeuronBox.appendChild(circle)
        inputElements[i] = new InputElement(circle, line)
    }

    var textbg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    textbg.setAttributeNS(null, 'id', "backgroundtexti");
    textbg.setAttributeNS(null, 'fill', "white");
    svg.appendChild(textbg);
    var text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttributeNS(null, 'id', "texti");
    svg.appendChild(text);

    weightElement = new SVGTextWithBg(text, textbg)

    selectInputNeuron(inputElements[0].circle)
}



function setOutpuNeurons() {
    output = []
    components.forEach((item, i, self) => output[i] = item.output);

    firstCircle = null
    offsetOutput = 0
    if (Math.min(output) < 0) {
        offsetOutput = Math.min(...output) * -1
    }
    maxOutputValue = Math.max(...output)
    outputLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    outputLine.setAttribute('id', "XXXXXXXXXx")
    outputLine.setAttribute('x1', '0');
    outputLine.setAttribute('y1', '0');
    outputLine.setAttribute('x2', '200');
    outputLine.setAttribute('y2', '200');
    outputLine.setAttribute("stroke", "black")
    outputLine.style.visibility = "visible"
    svg.appendChild(outputLine)
    for (var i = 0; i < output.length; i++) {

        var circle = document.createElement("div");
        circle.className = "circle"
        circle.setAttribute("onmouseover", "selectOutputNeuron(this)")
        bgColor = perc2color((offsetOutput + output[i]) / (offsetOutput + maxOutputValue))
        circle.style.backgroundColor = bgColor
        circle.style.color = getContrastYIQ(bgColor)
        var span = document.createElement('span');
        span.textContent = output[i].toFixed(4);;
        circle.appendChild(span);
        outputNeuronBox.appendChild(circle)
        outputElements[i] = circle
    }
    selectOutputNeuron(outputElements[0])
}




function onScrollInput() {
    for (var i = 0; i < inputElements.length; i++) {
        line = inputElements[i].line
        elemRect = inputElements[i].circle.getBoundingClientRect()
        bodyRect = outerBox.getBoundingClientRect();
        if (elemRect.top - bodyRect.top + inputElements[i].circle.clientHeight / 2 < 0 || elemRect.top - bodyRect.top + inputElements[i].circle.clientHeight / 2 > inputNeuronBox.clientHeight) {
            line.style.visibility = "hidden"
        } else {
            line.style.visibility = "visible"
            line.x1.baseVal.value = elemRect.left - bodyRect.left + inputElements[i].circle.clientWidth / 2
            line.y1.baseVal.value = elemRect.top - bodyRect.top + inputElements[i].circle.clientHeight / 2
            line.x2.baseVal.value = svg.clientWidth / 2
            line.y2.baseVal.value = inputNeuronBox.clientHeight / 2
        }
    }
    elemRect = inputElements[selectedIN].circle.getBoundingClientRect()
    bodyRect = outerBox.getBoundingClientRect();

    weightElement.text.setAttributeNS(null, "x", elemRect.left - bodyRect.left + inputElements[selectedIN].circle.clientWidth + 20)
    weightElement.text.setAttributeNS(null, "y", elemRect.top - bodyRect.top + inputElements[selectedIN].circle.clientHeight / 2)

    textbox = weightElement.text.getBBox();
    if (elemRect.top - bodyRect.top + inputElements[selectedIN].circle.clientHeight / 2 < textbox.height) {
        weightElement.text.setAttributeNS(null, "y", textbox.height)
        textbox = weightElement.text.getBBox();
    }
    if (elemRect.top - bodyRect.top + inputElements[selectedIN].circle.clientHeight / 2 > inputNeuronBox.clientHeight) {
        weightElement.text.setAttributeNS(null, "y", inputNeuronBox.clientHeight)
        textbox = weightElement.text.getBBox();
    }
    weightElement.background.setAttribute("x", textbox.x);
    weightElement.background.setAttribute("y", textbox.y);
    weightElement.background.setAttribute("width", textbox.width);
    weightElement.background.setAttribute("height", textbox.height);

}

function onScrollOutput() {
    elemRect = outputElements[selectedON].getBoundingClientRect()
        // if (elemRect.top - bodyRect.top + inputElements[i].circle.clientHeight / 2 < 0 || elemRect.top - bodyRect.top + inputElements[i].circle.clientHeight / 2 > inputNeuronBox.clientHeight) {
        //     outputLine.style.visibility = "hidden"
        // }
        // else {
    bodyRect = outerBox.getBoundingClientRect();
    if (elemRect.top - bodyRect.top + outputElements[selectedON].clientHeight / 2 < 0 || elemRect.top - bodyRect.top + outputElements[selectedON].clientHeight / 2 > outputNeuronBox.clientHeight) {
        outputLine.style.visibility = "hidden"
    } else {
        outputLine.style.visibility = "visible"

        outputLine.x2.baseVal.value = elemRect.left - bodyRect.left + outputElements[selectedON].clientWidth / 2
        outputLine.y2.baseVal.value = elemRect.top - bodyRect.top + outputElements[selectedON].clientHeight / 2
        outputLine.x1.baseVal.value = svg.clientWidth / 2
        outputLine.y1.baseVal.value = outputNeuronBox.clientHeight / 2
    }
    // }

}

function perc2color(perc) {
    perc = perc * 100
    var r, g, b = 0;
    if (perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
    } else {
        g = 255;
        r = Math.round(510 - 5.10 * perc);
    }
    var h = r * 0x10000 + g * 0x100 + b * 0x1;
    return '#' + ('000000' + h.toString(16)).slice(-6);
}

function getContrastYIQ(hexcolor) {
    hexcolor = hexcolor.replace("#", "");
    var r = parseInt(hexcolor.substr(0, 2), 16);
    var g = parseInt(hexcolor.substr(2, 2), 16);
    var b = parseInt(hexcolor.substr(4, 2), 16);
    var yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
    return (yiq >= 128) ? 'black' : 'white';
}

function selectInputNeuron(item) {
    for (var i = 0; i < inputElements.length; i++) {

        elemRect = inputElements[i].circle.getBoundingClientRect()


        if (inputElements[i].circle != item) {
            inputElements[i].circle.style.height = unselectedNeuronHeight
            inputElements[i].circle.style.width = unselectedNeuronHeight
            inputElements[i].circle.firstChild.style.visibility = 'hidden'
        } else {

            inputElements[i].circle.style.width = selectedNeuronHeight
            inputElements[i].circle.style.height = selectedNeuronHeight
            inputElements[i].circle.firstChild.style.visibility = 'visible'
            selectedIN = i
        }
    }


    weightElement.text.textContent = "*" + weights[selectedON][selectedIN].toFixed(4);
    onScrollInput();

}

function selectOutputNeuron(item) {
    for (var i = 0; i < outputElements.length; i++) {
        if (outputElements[i] != item) {
            outputElements[i].style.height = unselectedNeuronHeight
            outputElements[i].style.width = unselectedNeuronHeight
            outputElements[i].firstChild.style.visibility = 'hidden'
        } else {
            outputElements[i].style.width = selectedNeuronHeight
            outputElements[i].style.height = selectedNeuronHeight
            outputElements[i].firstChild.style.visibility = 'visible'
            selectedON = i
        }
    }
    onScrollOutput()
    weightElement.text.textContent = "*" + weights[selectedON][selectedIN].toFixed(4);

    textbox = weightElement.text.getBBox();
    weightElement.background.setAttribute("x", textbox.x);
    weightElement.background.setAttribute("y", textbox.y);
    weightElement.background.setAttribute("width", textbox.width);
    weightElement.background.setAttribute("height", textbox.height);
    biasElement.innerHTML = "&Sigma; +" + components[selectedON].bias.toFixed(4);

}