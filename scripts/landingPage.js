
// data problem section
const dataProblem = document.getElementById('data-problem');

const firstChild= dataProblem.children[0];
const secondChild= dataProblem.children[1];

firstChild.style.width = '450px';
firstChild.style.height = '300px';
firstChild.style.backgroundColor = '#EBEAEA';

secondChild.style.width='250px';
secondChild.style.height='300px';

// benefit section
const desc = document.querySelectorAll('.benefit-desc');
const img = document.querySelectorAll('.img-benefit');

if(desc[1]){
    const parent = desc[1].parentElement;

    parent.style.display = 'grid';
    parent.style.gridTemplateColumns = '1fr 1fr';
    parent.style.gridTemplateRows='1fr';
    parent.style.alignItems='center';
    parent.style.minHeight = '400px';
    parent.style.gap = '50px';
    
    // Setup child element
    desc[1].style.gridColumn = '2';
    desc[1].style.gridRow ='1';
    desc[1].style.display = 'flex';
    desc[1].style.flexDirection = 'column';
    desc[1].style.justifyContent = 'center'; // vertical center
}
if(img[1]){
    img[1].style.gridColumn='1';
    img[1].style.alignSelf='center';
}


