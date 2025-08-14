// color selected navbar menu
// const currentPath = window.location.pathname.split("/").pop(); // ambil nama file HTML
// const links = document.querySelectorAll(".nav-links a");

// console.log(`${currentPath} -> links= ${links}`)

// links.forEach(link => {
//     const dataPage = link.getAttribute("data-page");
//     const href = link.getAttribute("href").split("/").pop();
    
//     if (href === currentPath) {
//       link.classList.add("active");
//     } 
//     // else if(dataPage=='analisis'){
//     //     link.classList.add('active');
//     //     console.log(`active edit-> analisis : ${link.textContent}`);
//     // }
//     else {
//       link.classList.remove("active");
//     }
// });

// toggle-logo & navlinks
// const toggle = document.querySelector('.toggle-logo');
// const navLinks = document.querySelector('.nav-links');

// toggle.addEventListener('click', ()=>{
//     toggle.classList.toggle('active');
//     console.log('Toggle clicked: ', toggle.classList.contains('active'))
// });


// color selected navbar menu
const currentPath = window.location.pathname.split("/").pop(); // ambil nama file HTML
const links = document.querySelectorAll(".nav-links a");
const fromPage = new URLSearchParams(window.location.search).get("from_page");

console.log(`currentPath = ${currentPath}, fromPage = ${fromPage}`);
console.log(`${currentPath} -> links= ${links}`)

links.forEach(link => {
    const dataPage = link.getAttribute("data-page");
    const href = link.getAttribute("href").split("/").pop();
    
    if (href === currentPath) {
        link.classList.add("active");
        console.log(`Active set for "${link.textContent}" (match href)`);
    }
    // buat kondisi khusus (detail.html dari page history.html)
    else if (fromPage && fromPage === dataPage) {
        link.classList.add("active");
        console.log(`Active set for "${link.textContent}" (from_page=${fromPage})`);
    }
    else {
        link.classList.remove("active");
        console.log(`Active removed for "${link.textContent}"`);
    }
});