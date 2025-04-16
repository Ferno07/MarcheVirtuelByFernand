"use strict";

document.addEventListener('DOMContentLoaded', DCL_callback);

function DCL_callback(event) {
    const page = document.body.getAttribute("data-page");

    if (page === "new_user"){
        const password1 = document.querySelector('#password1Input');
        const password2 = document.querySelector('#password2Input');
        const button = document.querySelector('#soumission')
        button.disabled=true;
        password2.addEventListener("input", function() {
        if (password1.value !== password2.value) {
            password2.style.backgroundColor = "red";
            button.disabled=true;

        } else {
            password2.style.backgroundColor = "white";
            button.disabled=false;
        }
    }
    );
    }

    else if (page === "login"){
        const username = document.querySelector('#nameInput');
        const password = document.querySelector('#passwordInput');
        const button = document.querySelector('#connexion');
        button.disabled = true;

        function checkLogin() {
            // Active le bouton si les deux champs sont remplis
            if (username.value !== "" && password.value !== "") {
                button.disabled = false;
            } else {
                button.disabled = true;
            }
        }

        username.addEventListener("input", checkLogin);
        password.addEventListener("input", checkLogin);

       

    }
    else if (page === "index" || page === "header") {
   

        const accroche = document.querySelector('#accroche');
        let i = 0;
        let messages = ["Découvrez le savoir-faire authentique des zones reculées – une plateforme qui met en lumière artisans, commerçants et créateurs de villages pour vous offrir le meilleur de leur talent."

, "Connectez-vous et explorez l'univers unique des zones reculées : des entreprises locales passionnées vous invitent à découvrir leur savoir-faire et leurs produits authentiques.", "Brisez les frontières du quotidien ! Rejoignez notre réseau où les talents des zones reculées dévoilent leur créativité et où vous trouverez des produits et services d'exception.",
"Plongez dans l'univers des zones reculées – une vitrine digitale qui réunit entrepreneurs locaux et clients passionnés, pour un échange authentique et inspirant."];
        console.log("Élément accroche :", accroche);
        setInterval(() => {
        
            if (i == messages.length -1) {
                i=0;
                accroche.innerText = messages[0];
            } else {
                i=i+1
                accroche.innerText = messages[i];
            }
        }, 3000);
    }
    
    
   
}
