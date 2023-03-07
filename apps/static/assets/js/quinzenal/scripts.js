/* as datas são do tipo date, caso os meses sejam diferentes faça com que 
  apareça um alert avisando que os meses devem ser iguais, caso os meses sejam iguais
  a requisão deve continuar normalmente */
const data_inicio = document.querySelector("input#data-inicio").value;
const data_fim = document.querySelector("input#data-fim").value;
window.document.querySelector("button#btn-submit").addEventListener("click", function (event) {
  event.preventDefault();
  const mes_inicio = data_inicio.split("-")[1];
  const mes_fim = data_fim.split("-")[1];
  if (mes_inicio !== mes_fim) { alert("Meses devem ser iguais") }
})