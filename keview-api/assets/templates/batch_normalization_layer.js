var table = document.createElement("table")
table.id = "kernel_table"
var neuronalWeights

function onload(neuronalWeightsStr) {

    neuronalWeights = JSON.parse(neuronalWeightsStr)

    setInfo(0)
}

function updateInfo(x) {
    var index = x.src.split("_")[3]
    setInfo(index)

}

function setInfo(index) {
    document.getElementById("container").innerHTML = "&beta;= " + neuronalWeights[index].beta.toFixed(4) + "<br/>&gamma;= " + neuronalWeights[index].gamma.toFixed(4) + "<br/>&mu;= " + neuronalWeights[index].mean.toFixed(4) + " (mean)<br/>&sigma;= " + neuronalWeights[index].variance.toFixed(4) + " (variance)"
}