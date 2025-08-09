
// cek status login
function checkLoginStatus(){
    // GANTI ke server session - link dengan flask
    // return local
}

// color selected navbar menu
const currentPath = window.location.pathname.split("/").pop(); // ambil nama file HTML
const links = document.querySelectorAll(".nav-links a");

console.log(`${currentPath} -> links= ${links}`)

links.forEach(link => {
    const dataPage = link.getAttribute("data-page");
    const href = link.getAttribute("href").split("/").pop();
    
    if (href === currentPath) {
      link.classList.add("active");
    } 
    // else if(dataPage=='analisis'){
    //     link.classList.add('active');
    //     console.log(`active edit-> analisis : ${link.textContent}`);
    // }
    else {
      link.classList.remove("active");
    }
});