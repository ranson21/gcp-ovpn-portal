// tabs.js
export function showTab(tabName) {
  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.classList.remove("active");
  });
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.remove("active");
  });
  document.getElementById(tabName).classList.add("active");
  document
    .querySelector(`button[onclick="showTab('${tabName}')"]`)
    .classList.add("active");
}
