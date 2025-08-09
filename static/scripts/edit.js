// edit -> perbarui data
const updateButton = document.getElementById('update-device-btn');


if(updateButton){
    updateButton.addEventListener('click', function(e){
        // logic update data disini
        window.location.href='/analisis.html';
    
    });
}
else{
    console.error('update button NOT FOUND');
}