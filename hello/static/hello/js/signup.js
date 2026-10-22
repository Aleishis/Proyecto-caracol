document.querySelector('form').addEventListener('submit', function (e) {


    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password != confirmPassword){
        e.preventDefault(); //Esto es para que no se manden los datos del form
        alert("Passwords don't match");
    }

});
