function createConsole(console) {
  // Inject stylesheet.
  const linkElement = document.createElement("link");
  linkElement.href = import.meta.url.replace(".js", ".css");
  linkElement.rel = "stylesheet";
  document.head.append(linkElement);
  // Generate board.

  const spanElement = document.createElement("span");
  spanElement.className = "command";
  const inputElement = document.createElement("input")
    inputElement.type = "text"
    spanElement.append(inputElement)

    console.append(spanElement)
}

export { createConsole};