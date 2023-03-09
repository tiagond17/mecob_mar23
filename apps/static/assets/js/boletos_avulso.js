/* static/ts/scripts.js */
const messageErrors = window.document.querySelector("div.message-errors");

const listTodos = window.document.querySelector("div.list-todos");

const RESPONSE_IS_READY_CODE = 4

/* listener para adição de novo todo */
window.document.getElementById("form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const xhr = new XMLHttpRequest();
  const actionURL = event.target.action;
  xhr.open("POST", actionURL, true);
  xhr.onreadystatechange = () => {
    if (xhr.readyState === RESPONSE_IS_READY_CODE) {
      const response = JSON.parse(xhr.response);
      if (xhr.status === 200) {
        if (response.success === true) {
          messageErrors.innerHTML = ''
          addTodo(JSON.parse(response.todo));
        }
      } else {
        messageErrors.innerHTML = Object.values(response.errors)
        console.log("status", xhr.status, xhr.statusText);
      }
    }
  };
  xhr.send(form);
});