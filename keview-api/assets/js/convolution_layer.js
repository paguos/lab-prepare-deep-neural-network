var table = document.createElement("table")
document.getElementById("container").appendChild(table);
table.id = "kernel_table"

kernel_bias = document.getElementById("kernel_bias")

function onload(neuronalWeightsStr) {
    neuronalWeights = JSON.parse(neuronalWeightsStr)
    setKernel(0)
}

function updateKernel(x) {

    var index = x.src.split("_")[2]
    setKernel(index)

}

function setKernel(index) {
    table.innerHTML = "";
    for (var i of neuronalWeights[index].weights[0]) {
        var row = table.insertRow();
        for (var x of i) {
            var cell = row.insertCell();
            cell.innerHTML = x.toFixed(4);
        }
    }
    kernel_bias.innerHTML = "Bias: " + neuronalWeights[index].bias.toFixed(4)
}